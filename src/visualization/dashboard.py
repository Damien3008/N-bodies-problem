import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import numpy as np
from ..physics.integrators import EulerIntegrator, RK4Integrator, VerletIntegrator, AdamsBashforthIntegrator
from ..physics.equations import n_body_derivative
from ..data.celestial_bodies import SystemData

# Define some styling constants
COLORS = {
    'background': '#1f2630',
    'text': '#7fafdf',
    'grid': '#1f2630',
    'paper': '#2d3339',
}

PLOT_LAYOUT = {
    'paper_bgcolor': COLORS['paper'],
    'plot_bgcolor': COLORS['background'],
    'font': {'color': COLORS['text']},
    'showlegend': True,
}

class NBodyDashboard:
    # Move METHOD_INFO inside the class as a class attribute
    METHOD_INFO = {
        'euler': {
            'description': 'Simple first-order method. Fast but least accurate.',
            'precision': 'Low precision',
            'color': '#ff9800'  # Orange for low precision
        },
        'rk4': {
            'description': 'Fourth-order method with good stability. Excellent balance of speed and accuracy.',
            'precision': 'High precision',
            'color': '#4CAF50'  # Green for high precision
        },
        'verlet': {
            'description': 'Symplectic integrator that conserves energy well. Great for orbital mechanics.',
            'precision': 'High precision',
            'color': '#4CAF50'  # Green for high precision
        },
        'adams': {
            'description': 'Multi-step method using previous solutions. Good for smooth systems.',
            'precision': 'Medium precision',
            'color': '#2196F3'  # Blue for medium precision
        }
    }

    def __init__(self):
        self.app = dash.Dash(
            __name__,
            meta_tags=[
                {"name": "viewport", "content": "width=device-width, initial-scale=1"}
            ]
        )
        self.app.title = "N-Body Simulation"
        self.system = None
        self.current_results = None
        self.setup_layout()
        self.setup_callbacks()
    
    def create_control_panel(self):
        return html.Div([
            html.H3("Simulation Controls", className='control-title'),
            
            html.Label("Select System:", className='control-label'),
            dcc.Dropdown(
                id='system-dropdown',
                options=[
                    {'label': 'Solar System', 'value': 'solar system'},
                    {'label': 'Voyager 1', 'value': 'Voyager 1'},
                    {'label': 'Voyager 2', 'value': 'Voyager 2'},
                    {'label': 'Halley Comet', 'value': 'halley'}
                ],
                value='solar system',
                className='control-dropdown'
            ),
            
            html.Label("View Type:", className='control-label'),
            dcc.RadioItems(
                id='view-type',
                options=[
                    {'label': '2D View', 'value': '2d'},
                    {'label': '3D View', 'value': '3d'}
                ],
                value='3d',
                className='view-selector'
            ),
            
            html.Div([
                html.Label("Integration Method:", className='control-label'),
                html.Div([
                    html.Div([
                        html.Button(
                            ['Euler ', html.I(className="fas fa-info-circle")],  # Note the space after 'Euler'
                            id='euler-button',
                            className='method-button',
                            n_clicks=0
                        ),
                        html.Span(
                            self.METHOD_INFO['euler']['description'] + 
                            f" ({self.METHOD_INFO['euler']['precision']})",
                            className='method-tooltip'
                        )
                    ], className='method-button-container'),
                    
                    html.Div([
                        html.Button(
                            ['RK4 ', html.I(className="fas fa-info-circle")],
                            id='rk4-button',
                            className='method-button active',
                            n_clicks=0
                        ),
                        html.Span(
                            self.METHOD_INFO['rk4']['description'] + 
                            f" ({self.METHOD_INFO['rk4']['precision']})",
                            className='method-tooltip'
                        )
                    ], className='method-button-container'),
                    
                    html.Div([
                        html.Button(
                            ['Verlet ', html.I(className="fas fa-info-circle")],
                            id='verlet-button',
                            className='method-button',
                            n_clicks=0
                        ),
                        html.Span(
                            self.METHOD_INFO['verlet']['description'] + 
                            f" ({self.METHOD_INFO['verlet']['precision']})",
                            className='method-tooltip'
                        )
                    ], className='method-button-container'),
                    
                    html.Div([
                        html.Button(
                            ['Adams ', html.I(className="fas fa-info-circle")],
                            id='adams-button',
                            className='method-button',
                            n_clicks=0
                        ),
                        html.Span(
                            self.METHOD_INFO['adams']['description'] + 
                            f" ({self.METHOD_INFO['adams']['precision']})",
                            className='method-tooltip'
                        )
                    ], className='method-button-container'),
                    
                    # Hidden store for current method
                    dcc.Store(id='current-method', data='rk4')
                ], className='method-buttons-group'),
            ], className='method-container'),
            
            html.Div([
                html.Div([
                    html.Label("Time (days):", className='param-label'),
                    dcc.Input(
                        id='time-input',
                        type='number',
                        value=365,
                        min=1,
                        className='param-input'
                    ),
                ], className='param-group'),
                
                html.Div([
                    html.Label("Step Size (days):", className='param-label'),
                    dcc.Input(
                        id='step-input',
                        type='number',
                        value=1,
                        min=0.01,
                        step=0.01,
                        className='param-input'
                    ),
                ], className='param-group'),
            ], className='parameters-container'),
            
            html.Button(
                'Run Simulation',
                id='run-button',
                className='run-button'
            ),
            
            html.Div([
                html.Label("Animation Controls:", className='control-label'),
                html.Div([
                    html.Button(
                        'Play Animation',
                        id='animate-button',
                        className='animate-button'
                    ),
                    html.Div([
                        html.Label("Speed:", className='speed-label'),
                        dcc.Slider(
                            id='speed-slider',
                            min=0,
                            max=3,
                            step=1,
                            value=1,
                            marks={
                                0: '×0.5',
                                1: '×1',
                                2: '×2',
                                3: '×4'
                            },
                            className='speed-slider'
                        ),
                    ], className='speed-control')
                ], className='animation-controls'),
            ], className='animation-container'),
            
            html.Div(id='simulation-status', className='status-message'),
        ], className='control-panel')

    def setup_layout(self):
        self.app.layout = html.Div([
            html.H1("N-Body Simulation Dashboard", className='dashboard-title'),
            
            html.Div([
                html.Div([
                    self.create_control_panel()
                ], className='left-panel'),
                
                html.Div([
                    dcc.Graph(
                        id='trajectory-plot',
                        className='trajectory-plot'
                    ),
                    dcc.Interval(
                        id='animation-interval',
                        interval=100,  # base interval in milliseconds
                        disabled=True
                    ),
                    dcc.Store(id='animation-frame', data=0),
                    dcc.Store(id='simulation-data'),
                    dcc.Store(id='frame-skip', data=1),  # Store frame skip value
                ], className='right-panel'),
            ], className='main-content'),
            
            dcc.Loading(
                id="loading",
                type="circle",
                children=html.Div(id="loading-output")
            ),
        ], className='dashboard-container')
    
    def run_simulation(self, system_name, method, sim_time, step):
        t = np.arange(0, sim_time, step)
        self.system = SystemData(system_name)
        initial_state = self.system.get_initial_state()
        masses = self.system.get_masses()
        
        integrators = {
            'euler': EulerIntegrator,
            'rk4': RK4Integrator,
            'verlet': VerletIntegrator,
            'adams': AdamsBashforthIntegrator
        }
        
        integrator = integrators[method](
            lambda t, y: n_body_derivative(t, y, masses),
            step
        )
        
        n_bodies = len(masses)
        results = np.zeros((len(t), 6*n_bodies))
        results[0] = initial_state
        
        for i in range(1, len(t)):
            results[i] = integrator.step(t[i], results[i-1])
            
        return t, results
    
    def setup_callbacks(self):
        @self.app.callback(
            [Output('animation-interval', 'interval'),
             Output('frame-skip', 'data')],
            [Input('speed-slider', 'value')]
        )
        def update_animation_speed(speed_value):
            # Convert speed slider value to interval and frame skip
            speed_mappings = {
                0: (200, 1),   # ×0.5 speed
                1: (100, 1),   # ×1 speed
                2: (100, 2),   # ×2 speed
                3: (100, 4)    # ×4 speed
            }
            interval, frame_skip = speed_mappings[speed_value]
            return interval, frame_skip

        @self.app.callback(
            [Output('current-method', 'data'),
             Output('euler-button', 'className'),
             Output('rk4-button', 'className'),
             Output('verlet-button', 'className'),
             Output('adams-button', 'className')],
            [Input('euler-button', 'n_clicks'),
             Input('rk4-button', 'n_clicks'),
             Input('verlet-button', 'n_clicks'),
             Input('adams-button', 'n_clicks')]
        )
        def update_method_selection(*args):
            ctx = dash.callback_context
            if not ctx.triggered:
                return 'rk4', 'method-button', 'method-button active', 'method-button', 'method-button'
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            method_map = {
                'euler-button': 'euler',
                'rk4-button': 'rk4',
                'verlet-button': 'verlet',
                'adams-button': 'adams'
            }
            
            selected_method = method_map[button_id]
            button_classes = {
                method: 'method-button active' if method == selected_method else 'method-button'
                for method in ['euler', 'rk4', 'verlet', 'adams']
            }
            
            return (selected_method,
                    button_classes['euler'],
                    button_classes['rk4'],
                    button_classes['verlet'],
                    button_classes['adams'])

        @self.app.callback(
            [Output('trajectory-plot', 'figure'),
             Output('simulation-data', 'data'),
             Output('simulation-status', 'children'),
             Output('animation-frame', 'data'),
             Output('animation-interval', 'disabled'),
             Output('animate-button', 'children')],
            [Input('run-button', 'n_clicks'),
             Input('animation-interval', 'n_intervals'),
             Input('animate-button', 'n_clicks'),
             Input('view-type', 'value')],
            [State('system-dropdown', 'value'),
             State('current-method', 'data'),
             State('time-input', 'value'),
             State('step-input', 'value'),
             State('animation-frame', 'data'),
             State('simulation-data', 'data'),
             State('animation-interval', 'disabled'),
             State('frame-skip', 'data')]
        )
        def update_dashboard(run_clicks, n_intervals, animate_clicks, view_type,
                           system_name, method, sim_time, step, frame, sim_data, 
                           animation_disabled, frame_skip):
            
            ctx = dash.callback_context
            if not ctx.triggered:
                empty_fig = go.Figure(layout=PLOT_LAYOUT)
                return empty_fig, None, "", 0, True, "Play Animation"
            
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            # Handle Run Simulation button
            if trigger_id == 'run-button':
                if run_clicks is None:
                    empty_fig = go.Figure(layout=PLOT_LAYOUT)
                    return empty_fig, None, "", 0, True, "Play Animation"
                
                try:
                    t, results = self.run_simulation(system_name, method, sim_time, step)
                    self.current_results = results
                    
                    fig = self.create_figure(results, system_name, view_type)
                    
                    status_message = html.Div([
                        html.Span("✓ Simulation completed successfully", style={'color': '#00ff00'}),
                        html.Br(),
                        html.Span(f"Method: {method.upper()}, Duration: {sim_time} days")
                    ])
                    
                    return (fig, 
                           {'results': results.tolist(), 'names': [b.name for b in self.system.bodies]},
                           status_message,
                           0,  # Reset animation frame
                           True,  # Disable animation
                           "Play Animation")
                
                except Exception as e:
                    empty_fig = go.Figure(layout=PLOT_LAYOUT)
                    error_message = html.Div([
                        html.Span("⚠ Error in simulation", style={'color': '#ff0000'}),
                        html.Br(),
                        html.Span(str(e))
                    ])
                    return empty_fig, None, error_message, 0, True, "Play Animation"
            
            # Handle Animation Play/Pause button
            elif trigger_id == 'animate-button':
                if animate_clicks is None:
                    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, True, "Play Animation"
                
                new_disabled = not animation_disabled
                button_text = "Pause Animation" if animation_disabled else "Play Animation"
                return dash.no_update, dash.no_update, dash.no_update, frame, new_disabled, button_text
            
            # Handle Animation Interval or View Type change
            elif trigger_id in ['animation-interval', 'view-type']:
                if sim_data is None:
                    return dash.no_update, dash.no_update, dash.no_update, frame, dash.no_update, dash.no_update
                
                results = np.array(sim_data['results'])
                names = sim_data['names']
                
                # Update frame with frame_skip
                frame = frame + frame_skip if frame + frame_skip < len(results) else 0
                
                fig = self.create_animation_frame(results, names, frame, view_type)
                return fig, sim_data, dash.no_update, frame, dash.no_update, dash.no_update
            
            return dash.no_update

    def create_figure(self, results, system_name, view_type):
        fig = go.Figure()
        
        # Define size scale based on mass (larger mass = slightly larger marker)
        max_mass = max(body.mass for body in self.system.bodies)
        min_mass = min(body.mass for body in self.system.bodies)
        
        for i, body in enumerate(self.system.bodies):
            # Calculate relative size (log scale with minimum size)
            relative_size = max(4, 4 + 2 * np.log10((body.mass - min_mass) / (max_mass - min_mass) + 1e-10))
            
            if view_type == '3d':
                fig.add_trace(go.Scatter3d(
                    x=results[:, 3*i],
                    y=results[:, 3*i+1],
                    z=results[:, 3*i+2],
                    name=body.name,
                    mode='lines',
                    line=dict(
                        width=1,
                        color=f'hsl({(i * 360/len(self.system.bodies))}, 70%, 50%)'
                    ),
                    marker=dict(
                        size=float(relative_size),  # Convert to float
                        symbol='circle',
                        color=f'hsl({(i * 360/len(self.system.bodies))}, 70%, 50%)'
                    ),
                    hovertemplate=(
                        f"<b>{body.name}</b><br>" +
                        "X: %{x:.3f} AU<br>" +
                        "Y: %{y:.3f} AU<br>" +
                        "Z: %{z:.3f} AU<br>" +
                        f"Mass: {body.mass:.2e} M☉<extra></extra>"
                    )
                ))
            else:
                fig.add_trace(go.Scatter(
                    x=results[:, 3*i],
                    y=results[:, 3*i+1],
                    name=body.name,
                    mode='lines',
                    line=dict(
                        width=1,
                        color=f'hsl({(i * 360/len(self.system.bodies))}, 70%, 50%)'
                    ),
                    marker=dict(
                        size=float(relative_size),  # Convert to float
                        symbol='circle',
                        color=f'hsl({(i * 360/len(self.system.bodies))}, 70%, 50%)'
                    ),
                    hovertemplate=(
                        f"<b>{body.name}</b><br>" +
                        "X: %{x:.3f} AU<br>" +
                        "Y: %{y:.3f} AU<br>" +
                        f"Mass: {body.mass:.2e} M☉<extra></extra>"
                    )
                ))
        
        layout = {
            **PLOT_LAYOUT,
            'title': {
                'text': f'Trajectories - {system_name}',
                'font': {'size': 24},
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            'margin': {'l': 20, 'r': 20, 't': 80, 'b': 20}
        }
        
        if view_type == '3d':
            layout['scene'] = {
                'xaxis': {'title': 'X (AU)', 'gridcolor': COLORS['grid']},
                'yaxis': {'title': 'Y (AU)', 'gridcolor': COLORS['grid']},
                'zaxis': {'title': 'Z (AU)', 'gridcolor': COLORS['grid']},
                'camera': {
                    'up': {'x': 0, 'y': 0, 'z': 1},
                    'center': {'x': 0, 'y': 0, 'z': 0},
                    'eye': {'x': 1.5, 'y': 1.5, 'z': 1.5}
                }
            }
        else:
            layout.update({
                'xaxis': {'title': 'X (AU)', 'gridcolor': COLORS['grid']},
                'yaxis': {'title': 'Y (AU)', 'gridcolor': COLORS['grid']},
                'yaxis_scaleanchor': 'x'
            })
        
        fig.update_layout(layout)
        return fig

    def create_animation_frame(self, results, names, frame, view_type):
        fig = go.Figure()
        
        n_bodies = len(names)
        
        for i in range(n_bodies):
            marker_size = 6  # Fixed size for animation markers
            
            if view_type == '3d':
                # Add trail with gradient
                fig.add_trace(go.Scatter3d(
                    x=results[max(0, frame-50):frame+1, 3*i],
                    y=results[max(0, frame-50):frame+1, 3*i+1],
                    z=results[max(0, frame-50):frame+1, 3*i+2],
                    name=names[i],
                    mode='lines',
                    line=dict(
                        width=1,
                        color=f'hsl({(i * 360/n_bodies)}, 70%, 50%)',
                        dash='dot'
                    ),
                    opacity=0.5,
                    showlegend=False
                ))
                
                # Add current position
                fig.add_trace(go.Scatter3d(
                    x=[results[frame, 3*i]],
                    y=[results[frame, 3*i+1]],
                    z=[results[frame, 3*i+2]],
                    name=names[i],
                    mode='markers',
                    marker=dict(
                        size=marker_size,
                        symbol='circle',
                        color=f'hsl({(i * 360/n_bodies)}, 70%, 50%)'
                    ),
                    hovertemplate=(
                        f"<b>{names[i]}</b><br>" +
                        "X: %{x:.3f} AU<br>" +
                        "Y: %{y:.3f} AU<br>" +
                        "Z: %{z:.3f} AU<extra></extra>"
                    )
                ))
            else:
                # Add trail with gradient
                fig.add_trace(go.Scatter(
                    x=results[max(0, frame-50):frame+1, 3*i],
                    y=results[max(0, frame-50):frame+1, 3*i+1],
                    name=names[i],
                    mode='lines',
                    line=dict(
                        width=1,
                        color=f'hsl({(i * 360/n_bodies)}, 70%, 50%)',
                        dash='dot'
                    ),
                    opacity=0.5,
                    showlegend=False
                ))
                
                # Add current position
                fig.add_trace(go.Scatter(
                    x=[results[frame, 3*i]],
                    y=[results[frame, 3*i+1]],
                    name=names[i],
                    mode='markers',
                    marker=dict(
                        size=marker_size,
                        symbol='circle',
                        color=f'hsl({(i * 360/n_bodies)}, 70%, 50%)'
                    ),
                    hovertemplate=(
                        f"<b>{names[i]}</b><br>" +
                        "X: %{x:.3f} AU<br>" +
                        "Y: %{y:.3f} AU<br>" +
                        f"Time: {frame} days<extra></extra>"
                    )
                ))
        
        layout = {
            **PLOT_LAYOUT,
            'title': {
                'text': f'Time: {frame} days',
                'font': {'size': 24},
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            'margin': {'l': 20, 'r': 20, 't': 80, 'b': 20},
            'showlegend': True,
            'legend': {
                'x': 0,
                'y': 1,
                'bgcolor': 'rgba(45, 51, 57, 0.8)',
                'bordercolor': 'rgba(127, 175, 223, 0.3)',
                'borderwidth': 1
            }
        }
        
        if view_type == '3d':
            layout['scene'] = {
                'xaxis': {'title': 'X (AU)', 'gridcolor': COLORS['grid']},
                'yaxis': {'title': 'Y (AU)', 'gridcolor': COLORS['grid']},
                'zaxis': {'title': 'Z (AU)', 'gridcolor': COLORS['grid']},
                'camera': {
                    'up': {'x': 0, 'y': 0, 'z': 1},
                    'center': {'x': 0, 'y': 0, 'z': 0},
                    'eye': {'x': 1.5, 'y': 1.5, 'z': 1.5}
                }
            }
        else:
            layout.update({
                'xaxis': {'title': 'X (AU)', 'gridcolor': COLORS['grid']},
                'yaxis': {'title': 'Y (AU)', 'gridcolor': COLORS['grid']},
                'yaxis_scaleanchor': 'x'
            })
        
        fig.update_layout(layout)
        return fig

    def run_server(self, **kwargs):
        """
        Run the dashboard server with the specified configuration.
        
        Args:
            **kwargs: Keyword arguments to pass to the Dash app's run_server method
        """
        self.app.run_server(**kwargs) 