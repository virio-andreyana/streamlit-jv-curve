import streamlit as st
import math
import numpy as np
#from scipy.special import lambertw
import plotly.graph_objects as go

st.set_page_config(page_title="JV-Characterization", layout="wide")

diagram_dict = {'(Logarithmic) Dark JV Measurement':'log','(Simple) Proportioned JV-Curve':'simple','(Intermediate) with Fill Factor':'intermediate','(Complex) Shunt and Series Resistance':'complex'}

e = math.e
V = np.linspace(-5,10,1000)
I_ser = np.linspace(-50,10,10000)

with st.sidebar:

    st.title("JV-Characterization of the Solar Cells")

    diagram_long = st.selectbox(
        "Select a diagram",
        ['(Simple) Proportioned JV-Curve','(Intermediate) with Fill Factor','(Complex) Shunt and Series Resistance','(Logarithmic) Dark JV Measurement'])

    diagram = diagram_dict[diagram_long]

    if diagram == 'log':
        st.markdown("This is a JV-Curve where the X-axis is $V$ and the Y-axis is $I$. $V_{th}$ is a constant of 26 mV while $I_0$ is variable")
        Vth = 0.026 #V
        I0 = st.slider("Saturation Current in 10^-14 A/cm^2", min_value=1.00, max_value=10e7, step=1000.00, value=1.00)
        n = st.slider("Diode ideality factor", min_value=1.00, max_value=2.00, step=0.01, value=1.00 )
        Rp = st.slider("Parallel Resistance", min_value=1.00, max_value=10e3, step=1000.00, value=10e2 ) #5 ohm cm²
        Rs = st.slider("Series Resistance", min_value=0.00005, max_value=0.05, step=0.0001, value=0.00005 ) #5 ohm cm²

        I = I0/1e14*(e**(V/(n*Vth))-1)
        I_shunt = I0/1e14*(e**(V/(n*Vth))-1)+V/Rp
        V_ser = n*Vth*np.log((I_ser)/(I0/1e14))+I_ser*Rs


    elif diagram == 'simple':
        st.markdown("This is a JV-Curve where the X-axis is the proportion of $V/V_{Th}$ and the Y-axis is the proportion of $I/I_{0}$")

        Iph = st.slider("Photo Current / Saturation Current", min_value=0, max_value=100, step=1, value=0 )
        I = (e**(V)-1)-Iph

    elif diagram == 'intermediate' or 'complex':
        st.markdown("This is a JV-Curve where the X-axis is $V$ and the Y-axis is $I$. $V_{th}$ is a constant of 26 mV while $I_0$ is variable")
        Vth = 0.026 #V
        Iph = st.slider("Photo Current in A", min_value=0, max_value=50, step=1, value=0 )
        I0 = st.slider("Saturation Current in 10^-14 A/cm^2", min_value=1.00, max_value=10e7, step=1000.00, value=1.00)
        n = st.slider("Diode ideality factor", min_value=1.00, max_value=2.00, step=0.01, value=1.00 )
        Rs = st.slider("Series Resistance", min_value=0.00005, max_value=0.05, step=0.0001, value=0.00005 ) #5 ohm cm²
        Rp = st.slider("Parallel Resistance", min_value=0.01, max_value=2.00, step=0.01, value=2.00 ) #5 ohm cm²     

        # standard JV-curve
        I = I0/1e14*(e**(V/(n*Vth))-1)-Iph

        # for the shunt equation
        I_sh = I0/1e14*(e**(V/(n*Vth))-1)+V/Rp-Iph

        # for the series equation
        V_ser = n*Vth*np.log((I_ser+Iph)/(I0/1e14))+I_ser*Rs

st.title(diagram_long)

def add_layout(x_title,y_title,x_range,y_range,y_type):
    layout = dict(plot_bgcolor='white',
                margin=dict(t=20, l=20, r=20, b=20),
                xaxis=dict(title=x_title,
                     range=x_range,
                     linecolor='grey',
                     showgrid=True,
                     mirror=True),
                yaxis=dict(title=y_title,
                     range=y_range,
                     linecolor='#d9d9d9',
                     type=y_type,
                     showgrid=True,
                     mirror=True))
    return layout

def add_simple_figure(V,I,layout):

    fig = go.Figure(layout=layout)

    linespace = np.linspace(-100,100,1000)

    fig.add_trace(go.Scatter(x=linespace,y=0*linespace, name=""))
    fig.add_trace(go.Scatter(x=0*linespace,y=linespace, name=""))
    fig.update_traces(marker=dict(color='black'))
    fig.add_trace(go.Scatter(x=V,y=I, name="JV-curve"))

    st.plotly_chart(fig)


if diagram == 'log':
    st.latex(r'''I(V) = I_0 \cdot \left(e^\frac{V}{n \cdot V_{th}}-1 \right)''')
    st.markdown("When this equation is converted into a logarithmic scale:")
    st.latex(r'''ln(I) = ln(I_0) + \frac{1}{n \cdot V_{th}} \cdot V''')

    layout = add_layout('V','log I',[0, 5],[-15,5],'log')

    fig = go.Figure(layout=layout)

    linespace = np.linspace(-100,100,1000)

    fig.add_trace(go.Scatter(x=V,y=I_shunt, name="JV-curve with parallel resistance"))
    fig.add_trace(go.Scatter(x=V_ser,y=I_ser, name="JV-curve with series resistance"))
    fig.add_trace(go.Scatter(x=V,y=I, name="JV-curve"))

    st.plotly_chart(fig)

elif diagram == 'simple':
    st.latex(r'''I(V) = I_0 \cdot \left(e^\frac{qV}{kT}-1 \right)-I_{ph}''')
    layout = add_layout('qV/kT','I/I0',[-3, 10],[-100,100],"-")
    add_simple_figure(V,I,layout)

elif diagram == 'intermediate':
    st.latex(r'''I(V) = I_0 \cdot \left(e^\frac{V}{n \cdot V_{th}}-1 \right)-I_{ph}''')
    layout = add_layout('V','I',[-0.5, 2],[-50,10],"-")
    add_simple_figure(V,I,layout)
    
    Isc = -Iph
    Voc = n*Vth*np.log(1+Iph/(I0/1e14))

    # calculating voc and isc
    st.markdown("to find the short circuit current:")
    st.latex(r'''I_{SC} = -I_{ph}''')
    st.markdown("to find the open circuit voltage:")
    st.latex(r'''V_{OC} = n \cdot V_{th} \cdot ln \left(1+\frac{Iph}{I_0}\right)''')
    st.info(f"The open circuit voltage is : {round(Voc,3)} and the short circuit current is : {round(Isc,2)}")

    P = V*I
    Pmpp = np.amin(P)
    Impp = I[np.where(P==Pmpp)][0]
    Vmpp = V[np.where(P==Pmpp)][0]

    # calculating mpp
    st.markdown("to find power:")
    st.latex(r'''P(V)=V \cdot I''')
    st.info(f"The maximum power is : {round(-Pmpp,2)} where V are : {round(Vmpp,2)} and I are : {round(Impp,2)}")

    layout = add_layout('V','|P| and |I|',[-0, 2],[-0,50],"-")

    fig = go.Figure(layout=layout)

    fig.add_trace(go.Scatter(x=np.linspace(0,Vmpp,100),y=np.full(shape = 100, fill_value = -Impp), name="Impp"))
    fig.add_trace(go.Scatter(x=np.full(shape = 100, fill_value = Vmpp),y=np.linspace(0,-Impp,100), name="Vmpp"))
    fig.add_trace(go.Scatter(x=V,y=-I, name="JV-curve"))
    fig.add_trace(go.Scatter(x=V,y=-P, name="Power curve"))

    st.plotly_chart(fig)

    # calculating the fill factor
    st.markdown("The equation for Fill factor is:")
    st.latex(r'''FF = \frac{I_{mpp} \cdot V_{mpp}}{I_{sc} \cdot V_{oc}}''')
    FF = (Vmpp*Impp)/(Voc*Isc)
    st.info(f"The fill factor is: {round(FF*100,2)} %")


elif diagram == 'complex':

    st.markdown("The general equation for a current with shunt and series resistance is:")
    st.latex(r'''I(V) = I_0 \cdot \left(e^\frac{V-I \cdot R_s}{n \cdot V_{th}}-1 \right) + \frac{V-I \cdot R_s}{R_p}-I_{ph}''')
    st.markdown("When series resistance is minescules, the equation can be simplified as follow:")
    st.latex(r'''I(V) = I_0 \cdot \left(e^\frac{V}{n \cdot V_{th}}-1 \right) + \frac{V}{R_p}-I_{ph}''')

    layout = add_layout('V','I',[-0.5, 2],[-50,10],"-")

    fig = go.Figure(layout=layout)

    linespace = np.linspace(-100,100,1000)

    fig.add_trace(go.Scatter(x=linespace,y=0*linespace, name=""))
    fig.add_trace(go.Scatter(x=0*linespace,y=linespace, name=""))
    fig.update_traces(marker=dict(color='black'))
    fig.add_trace(go.Scatter(x=V,y=I_sh, marker=dict(color='blue'), name="JV-curve with parallel resistance"))
    fig.add_trace(go.Scatter(x=V,y=I, marker=dict(color='red'), name="JV-curve"))

    st.plotly_chart(fig)

    st.markdown("When parallel resistance is larger than 1000, the equation can be simplified as follow:")
    st.latex(r'''I(V) = I_0 \cdot \left(e^\frac{V-I \cdot R_s}{n \cdot V_{th}}-1 \right)-I_{ph}''')
    st.markdown("the equation can be inversed into the following:")
    st.latex(r'''V(I) = n \cdot Vth \cdot ln \left(\frac{I+I_{ph}}{I_0}\right)+I \cdot R_s''')

    fig = go.Figure(layout=layout)

    linespace = np.linspace(-100,100,1000)

    fig.add_trace(go.Scatter(x=linespace,y=0*linespace, name=""))
    fig.add_trace(go.Scatter(x=0*linespace,y=linespace, name=""))
    fig.update_traces(marker=dict(color='black'))
    fig.add_trace(go.Scatter(x=V_ser,y=I_ser,marker=dict(color='blue'), name="JV-curve with series resistance"))
    fig.add_trace(go.Scatter(x=V,y=I, marker=dict(color='red'), name="JV-curve"))
    
    st.plotly_chart(fig)

st.warning(":building_construction: Sorry, this page is still under construction")

