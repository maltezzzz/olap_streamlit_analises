import plotly.express as px
import plotly.graph_objects as go

def stacked_line(df):
    fig = px.line(df, markers=True)
    fig.update_layout(xaxis_title=df.index.name, yaxis_title="Valor")
    return fig

def heatmap(df):
    fig = px.imshow(df, aspect="auto", color_continuous_scale="Viridis")
    return fig

def horizontal_bar(df):
    fig = px.bar(df, orientation="h")
    return fig

def line_per_region(df):
    fig = px.line(df, markers=True)
    return fig

def grouped_bar(df):
    fig = px.bar(df, barmode="group")
    return fig

def area_stacked(df):
    fig = px.area(df)
    return fig

def horizontal_topN(df, top=20):
    df = df.sort_values(ascending=False).head(top)
    fig = px.bar(df, orientation="h")
    return fig

def line(df, title=None):
    fig = px.line(
        df,
        markers=True,
        title=title,
    )
    fig.update_layout(
        xaxis_title=df.index.name if df.index.name else "",
        yaxis_title=df.columns[0] if len(df.columns) == 1 else "",
        legend_title="",
        template="plotly_dark"
    )
    return fig
