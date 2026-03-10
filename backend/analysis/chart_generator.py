"""
backend/analysis/chart_generator.py
Professional chart generation using Matplotlib + Seaborn + Plotly
Like a data scientist would create them.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from scipy import stats
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
import io
import base64
import json
import warnings
warnings.filterwarnings("ignore")

# ── Professional dark theme ──────────────────────────────────────
DARK_BG = "#0d1117"
CARD_BG = "#161b22"
ACCENT = "#58a6ff"
GREEN = "#3fb950"
ORANGE = "#d29922"
RED = "#f85149"
PURPLE = "#bc8cff"
TEXT = "#c9d1d9"
MUTED = "#8b949e"
GRID = "#21262d"

PALETTE = [ACCENT, GREEN, ORANGE, PURPLE, RED, "#ff7b72", "#ffa657", "#79c0ff"]

def apply_dark_theme():
    plt.rcParams.update({
        "figure.facecolor": DARK_BG,
        "axes.facecolor": CARD_BG,
        "axes.edgecolor": GRID,
        "axes.labelcolor": TEXT,
        "axes.titlecolor": TEXT,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "text.color": TEXT,
        "grid.color": GRID,
        "grid.linewidth": 0.5,
        "axes.grid": True,
        "legend.facecolor": CARD_BG,
        "legend.edgecolor": GRID,
        "legend.labelcolor": TEXT,
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
    })

def fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight",
                facecolor=DARK_BG, edgecolor="none")
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return f"data:image/png;base64,{img_b64}"

def plotly_to_json(fig) -> str:
    return json.loads(fig.to_json())


class ChartGenerator:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        apply_dark_theme()

    # ─────────────────────────────────────────────
    # 1. DISTRIBUTION DASHBOARD (Matplotlib + Seaborn)
    # ─────────────────────────────────────────────
    def distribution_dashboard(self) -> str:
        cols = self.numeric_cols[:6]
        if not cols:
            return None

        n = len(cols)
        ncols = min(3, n)
        nrows = (n + ncols - 1) // ncols
        fig, axes = plt.subplots(nrows, ncols, figsize=(6 * ncols, 4 * nrows))
        fig.patch.set_facecolor(DARK_BG)

        if n == 1:
            axes = [axes]
        elif nrows == 1:
            axes = list(axes)
        else:
            axes = [ax for row in axes for ax in row]

        for i, col in enumerate(cols):
            ax = axes[i]
            data = self.df[col].dropna()
            color = PALETTE[i % len(PALETTE)]

            # KDE + histogram
            ax.hist(data, bins=30, color=color, alpha=0.3, density=True, edgecolor="none")
            data.plot.kde(ax=ax, color=color, linewidth=2.5)

            # Mean & median lines
            ax.axvline(data.mean(), color=GREEN, linestyle="--", linewidth=1.5, alpha=0.9, label=f"Mean: {data.mean():.2f}")
            ax.axvline(data.median(), color=ORANGE, linestyle=":", linewidth=1.5, alpha=0.9, label=f"Median: {data.median():.2f}")

            ax.set_title(f"{col}\nskew={data.skew():.2f}  kurt={data.kurtosis():.2f}")
            ax.set_xlabel("")
            ax.legend(fontsize=8, framealpha=0.5)
            ax.tick_params(labelsize=8)

        for j in range(i + 1, len(axes)):
            axes[j].set_visible(False)

        plt.suptitle("Distribution Analysis", y=1.01, fontsize=15, fontweight="bold", color=TEXT)
        plt.tight_layout()
        return fig_to_base64(fig)

    # ─────────────────────────────────────────────
    # 2. BOX PLOTS (outlier visualization)
    # ─────────────────────────────────────────────
    def boxplot_dashboard(self) -> str:
        cols = self.numeric_cols[:8]
        if not cols:
            return None

        fig, ax = plt.subplots(figsize=(max(10, len(cols) * 1.5), 6))
        fig.patch.set_facecolor(DARK_BG)

        data_to_plot = [self.df[col].dropna().values for col in cols]
        bp = ax.boxplot(data_to_plot, patch_artist=True, notch=False,
                        medianprops={"color": GREEN, "linewidth": 2.5},
                        whiskerprops={"color": MUTED, "linewidth": 1.5},
                        capprops={"color": MUTED, "linewidth": 1.5},
                        flierprops={"marker": "o", "markersize": 3, "alpha": 0.4})

        for patch, color in zip(bp["boxes"], PALETTE * 3):
            patch.set_facecolor(color)
            patch.set_alpha(0.4)
            patch.set_edgecolor(color)

        ax.set_xticks(range(1, len(cols) + 1))
        ax.set_xticklabels(cols, rotation=30, ha="right", fontsize=9)
        ax.set_title("Box Plot — Outlier Detection (IQR Method)", fontsize=13, fontweight="bold")
        plt.tight_layout()
        return fig_to_base64(fig)

    # ─────────────────────────────────────────────
    # 3. CORRELATION HEATMAP (Seaborn)
    # ─────────────────────────────────────────────
    def correlation_heatmap(self) -> str:
        cols = self.numeric_cols[:10]
        if len(cols) < 2:
            return None

        corr = self.df[cols].corr()
        mask = np.triu(np.ones_like(corr, dtype=bool))

        fig, ax = plt.subplots(figsize=(max(8, len(cols)), max(6, len(cols) * 0.9)))
        fig.patch.set_facecolor(DARK_BG)

        cmap = sns.diverging_palette(220, 20, as_cmap=True)
        sns.heatmap(corr, mask=mask, cmap=cmap, center=0,
                    annot=True, fmt=".2f", annot_kws={"size": 9, "color": TEXT},
                    linewidths=0.5, linecolor=GRID,
                    square=True, ax=ax,
                    cbar_kws={"shrink": 0.8})

        ax.set_title("Pearson Correlation Matrix", fontsize=13, fontweight="bold", pad=15)
        ax.tick_params(labelsize=9)
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        return fig_to_base64(fig)

    # ─────────────────────────────────────────────
    # 4. CATEGORICAL BAR CHARTS
    # ─────────────────────────────────────────────
    def categorical_charts(self) -> list:
        charts = []
        for col in self.categorical_cols[:4]:
            vc = self.df[col].value_counts().head(12)
            if len(vc) < 2:
                continue

            fig, axes = plt.subplots(1, 2, figsize=(14, 5))
            fig.patch.set_facecolor(DARK_BG)

            # Bar chart
            colors = [PALETTE[i % len(PALETTE)] for i in range(len(vc))]
            bars = axes[0].barh(vc.index[::-1], vc.values[::-1], color=colors[::-1], edgecolor="none", height=0.7)
            for bar, val in zip(bars, vc.values[::-1]):
                axes[0].text(bar.get_width() + max(vc.values) * 0.01, bar.get_y() + bar.get_height() / 2,
                             f"{val:,} ({val/len(self.df)*100:.1f}%)", va="center", fontsize=8, color=TEXT)
            axes[0].set_title(f"{col} — Frequency", fontweight="bold")
            axes[0].set_xlabel("Count")
            axes[0].tick_params(labelsize=9)

            # Pie chart
            wedge_colors = [PALETTE[i % len(PALETTE)] for i in range(len(vc))]
            wedges, texts, autotexts = axes[1].pie(
                vc.values, labels=None,
                colors=wedge_colors, autopct="%1.1f%%",
                pctdistance=0.75, startangle=90,
                wedgeprops={"edgecolor": DARK_BG, "linewidth": 2}
            )
            for autotext in autotexts:
                autotext.set_color(DARK_BG)
                autotext.set_fontsize(8)
                autotext.set_fontweight("bold")
            axes[1].legend(vc.index, loc="center left", bbox_to_anchor=(1, 0.5), fontsize=8, framealpha=0.3)
            axes[1].set_title(f"{col} — Distribution", fontweight="bold")

            plt.suptitle(f"Category Analysis: {col}", fontsize=13, fontweight="bold", color=TEXT)
            plt.tight_layout()
            charts.append({"column": col, "image": fig_to_base64(fig)})

        return charts

    # ─────────────────────────────────────────────
    # 5. SCATTER MATRIX (Seaborn pairplot style)
    # ─────────────────────────────────────────────
    def scatter_matrix(self) -> str:
        cols = self.numeric_cols[:4]
        if len(cols) < 2:
            return None

        # Use seaborn pairplot with custom colors
        color_col = self.categorical_cols[0] if self.categorical_cols else None
        n_categories = self.df[color_col].nunique() if color_col else 1

        if color_col and n_categories <= 8:
            g = sns.pairplot(
                self.df[cols + [color_col]].dropna().head(300),
                hue=color_col,
                palette=PALETTE[:n_categories],
                plot_kws={"alpha": 0.5, "s": 20},
                diag_kind="kde"
            )
        else:
            g = sns.pairplot(
                self.df[cols].dropna().head(300),
                plot_kws={"alpha": 0.4, "s": 20, "color": ACCENT},
                diag_kind="kde",
                diag_kws={"color": ACCENT, "fill": True, "alpha": 0.4}
            )

        g.fig.patch.set_facecolor(DARK_BG)
        for ax in g.axes.flatten():
            if ax:
                ax.set_facecolor(CARD_BG)
                ax.tick_params(colors=MUTED, labelsize=7)
                for spine in ax.spines.values():
                    spine.set_edgecolor(GRID)

        g.fig.suptitle("Scatter Matrix — Pairwise Relationships", y=1.01,
                        fontsize=13, fontweight="bold", color=TEXT)
        return fig_to_base64(g.fig)

    # ─────────────────────────────────────────────
    # 6. QQ PLOTS (normality check)
    # ─────────────────────────────────────────────
    def qq_plots(self) -> str:
        cols = self.numeric_cols[:4]
        if not cols:
            return None

        n = len(cols)
        ncols = min(2, n)
        nrows = (n + 1) // 2
        fig, axes = plt.subplots(nrows, ncols, figsize=(6 * ncols, 5 * nrows))
        fig.patch.set_facecolor(DARK_BG)

        if n == 1:
            axes = [axes]
        elif nrows == 1:
            axes = list(axes)
        else:
            axes = [ax for row in axes for ax in row]

        for i, col in enumerate(cols):
            ax = axes[i]
            data = self.df[col].dropna()
            (osm, osr), (slope, intercept, r) = stats.probplot(data, dist="norm")
            ax.plot(osm, osr, "o", color=PALETTE[i % len(PALETTE)], alpha=0.5, markersize=3)
            ax.plot(osm, slope * np.array(osm) + intercept, color=RED, linewidth=2, label=f"r²={r**2:.3f}")
            ax.set_title(f"Q-Q Plot: {col}", fontweight="bold")
            ax.set_xlabel("Theoretical Quantiles")
            ax.set_ylabel("Sample Quantiles")
            ax.legend(fontsize=9)

        for j in range(i + 1, len(axes)):
            axes[j].set_visible(False)

        plt.suptitle("Q-Q Plots — Normality Assessment", y=1.01, fontsize=13, fontweight="bold", color=TEXT)
        plt.tight_layout()
        return fig_to_base64(fig)

    # ─────────────────────────────────────────────
    # 7. VIOLIN PLOTS (distribution by category)
    # ─────────────────────────────────────────────
    def violin_plots(self) -> str:
        if not self.categorical_cols or not self.numeric_cols:
            return None

        cat_col = self.categorical_cols[0]
        num_cols = self.numeric_cols[:3]
        n_cats = self.df[cat_col].nunique()

        if n_cats > 12 or n_cats < 2:
            return None

        fig, axes = plt.subplots(1, len(num_cols), figsize=(6 * len(num_cols), 6))
        fig.patch.set_facecolor(DARK_BG)

        if len(num_cols) == 1:
            axes = [axes]

        palette = {cat: PALETTE[i % len(PALETTE)] for i, cat in enumerate(self.df[cat_col].unique())}

        for i, num_col in enumerate(num_cols):
            plot_data = self.df[[cat_col, num_col]].dropna()
            sns.violinplot(data=plot_data, x=cat_col, y=num_col,
                           palette=palette, ax=axes[i], inner="box",
                           linewidth=1.5, saturation=0.8)
            axes[i].set_title(f"{num_col} by {cat_col}", fontweight="bold")
            axes[i].tick_params(axis="x", rotation=30, labelsize=8)

        plt.suptitle(f"Violin Plots — Distribution by {cat_col}", fontsize=13, fontweight="bold", color=TEXT)
        plt.tight_layout()
        return fig_to_base64(fig)

    # ─────────────────────────────────────────────
    # 8. MISSING VALUES HEATMAP
    # ─────────────────────────────────────────────
    def missing_values_chart(self) -> str:
        missing = self.df.isnull().sum()
        missing = missing[missing > 0]

        if len(missing) == 0:
            return None

        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor(DARK_BG)

        colors = [RED if v / len(self.df) > 0.3 else ORANGE if v / len(self.df) > 0.1 else MUTED
                  for v in missing.values]
        bars = ax.barh(missing.index, missing.values / len(self.df) * 100,
                       color=colors, edgecolor="none", height=0.6)

        for bar, val in zip(bars, missing.values):
            ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                    f"{val:,} ({val/len(self.df)*100:.1f}%)", va="center", fontsize=9, color=TEXT)

        ax.axvline(10, color=ORANGE, linestyle="--", linewidth=1, alpha=0.7, label="10% threshold")
        ax.axvline(30, color=RED, linestyle="--", linewidth=1, alpha=0.7, label="30% critical")
        ax.set_xlabel("Missing %", fontsize=10)
        ax.set_title("Missing Values by Column", fontsize=13, fontweight="bold")
        ax.legend(fontsize=9)
        plt.tight_layout()
        return fig_to_base64(fig)

    # ─────────────────────────────────────────────
    # 9. PLOTLY — Interactive Scatter
    # ─────────────────────────────────────────────
    def interactive_scatter(self) -> dict:
        if len(self.numeric_cols) < 2:
            return None

        x, y = self.numeric_cols[0], self.numeric_cols[1]
        color_col = self.categorical_cols[0] if self.categorical_cols and self.df[self.categorical_cols[0]].nunique() <= 10 else None

        fig = px.scatter(
            self.df.dropna(subset=[x, y]),
            x=x, y=y, color=color_col,
            color_discrete_sequence=PALETTE,
            opacity=0.7,
            template="plotly_dark",
            title=f"Interactive Scatter: {x} vs {y}",
            trendline="ols" if not color_col else None,
            hover_data=self.df.columns.tolist()[:6]
        )
        fig.update_layout(
            paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG,
            font={"color": TEXT, "family": "monospace"},
            title_font_size=14
        )
        return plotly_to_json(fig)

    # ─────────────────────────────────────────────
    # 10. PLOTLY — Correlation Sunburst / Treemap
    # ─────────────────────────────────────────────
    def interactive_distribution(self) -> dict:
        if not self.numeric_cols:
            return None

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[f"Distribution: {col}" for col in self.numeric_cols[:4]],
            specs=[[{"type": "histogram"}, {"type": "histogram"}],
                   [{"type": "histogram"}, {"type": "histogram"}]]
        )

        positions = [(1,1),(1,2),(2,1),(2,2)]
        for i, (col, pos) in enumerate(zip(self.numeric_cols[:4], positions)):
            data = self.df[col].dropna()
            fig.add_trace(
                go.Histogram(x=data, name=col, marker_color=PALETTE[i], opacity=0.8, nbinsx=30),
                row=pos[0], col=pos[1]
            )

        fig.update_layout(
            template="plotly_dark", paper_bgcolor=DARK_BG,
            title_text="Interactive Distribution Charts",
            showlegend=True, height=600
        )
        return plotly_to_json(fig)

    # ─────────────────────────────────────────────
    # GENERATE ALL CHARTS
    # ─────────────────────────────────────────────
    def generate_all(self) -> dict:
        result = {}

        def safe(fn, key):
            try:
                val = fn()
                if val and not (isinstance(val, dict) and 'error' in val):
                    result[key] = val
            except Exception as e:
                import traceback
                print(f"Chart {key} failed: {e}")

        safe(self.distribution_dashboard, "distribution_dashboard")
        safe(self.boxplot_dashboard, "boxplot_dashboard")
        safe(self.correlation_heatmap, "correlation_heatmap")
        safe(self.scatter_matrix, "scatter_matrix")
        safe(self.qq_plots, "qq_plots")
        safe(self.violin_plots, "violin_plots")
        safe(self.missing_values_chart, "missing_values_chart")
        safe(self.interactive_scatter, "interactive_scatter")
        safe(self.interactive_distribution, "interactive_distribution")

        cat_charts = self.categorical_charts()
        if cat_charts:
            result["categorical_charts"] = cat_charts

        return result