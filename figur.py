import plotly.graph_objects as go

def figur(data):
    x = list(data.index)
    x_rev = x[::-1]
    
    # Line 1
    y1 = list(data.precipitation_amount)
    y1_upper = list(data.precipitation_amount_max)
    y1_lower = list(data.precipitation_amount_min)
    y1_lower = y1_lower[::-1]
    
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=x+x_rev,
        y=y1_upper+y1_lower,
        fill='toself',
        fillcolor='rgba(0,100,80,0.2)',
        line_color='rgba(255,255,255,0)',
        showlegend=False,
        
    ))
    
    fig.add_trace(go.Scatter(
        x=x, y=y1,
        line_color='rgb(0,100,80)',
        showlegend=False,
    ))
    fig.update_layout(width=915)
    fig.update_layout(title_text = "Nedbør")
    
    
    return fig