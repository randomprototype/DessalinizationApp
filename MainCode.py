"""
Victor Hugo Resende Lima
vhugoreslim@gmail.com

Esse código necessita dos seguintes pacotes nas respectivas versões:
Pillow==9.0.1
scipy==1.7.3
streamlit==1.5.0
click==8
"""
import streamlit as st
import numpy as np
from scipy.integrate import quad #Single integral
from scipy.integrate import dblquad
from PIL import Image

def main():
    #criando 3 colunas
    col1, col2, col3= st.columns(3)
    foto = Image.open('randomen.png')
    #st.sidebar.image("randomen.png", use_column_width=True)
    #inserindo na coluna 2
    col2.image(foto, use_column_width=True)
    #O código abaixo centraliza e atribui cor
    st.markdown("<h2 style='text-align: center; color: #306754;'>Maintenance Policy Cost Assessment for Reverse-Osmosis Desalination Systems</h2>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style="background-color: #F3F3F3; padding: 10px; text-align: center;">
          <p style="font-size: 20px; font-weight: bold;">Mathematical modelling of component dependencies in a multi-component system: planning maintenance of membranes in reverse-osmosis desalination</p>
          <p style="font-size: 15px;">By: Victor H. R. Lima & Rafael G. N. Paiva & Phuc Do & Cristiano A. V. Cavalcante & Frits van Rooij & Philip Scarf</p>
        </div>
        """, unsafe_allow_html=True)

    menu = ["Cost Assessment", "Information", "Website"]
    
    choice = st.sidebar.selectbox("Select here", menu)
    
    if choice == menu[0]:
        st.header(menu[0])
        if 'num_columns' not in st.session_state:
            st.session_state.num_columns = 2
        def add_column():
            st.session_state.num_columns += 1
        def remove_column():
            if st.session_state.num_columns > 1:
                st.session_state.num_columns -= 1
        
        st.subheader("Insert the parameter values below:")
        col1, col2, col3 = st.columns(3)

        with col1:
            Kappa1 = st.number_input(
                "Feed water quality parameter 1",
                min_value=0.0, value=0.0014, help=r"$\kappa_1$"
            )
            Beta = st.number_input(
                "Algae bloom dissipation rate",
                min_value=0.0, value=0.026, help=r"$\beta$"
            )
            Gamma = st.number_input(
                "Stochastic dependence strength",
                min_value=0.0, value=0.73, help=r"$\gamma$"
            )
            CS = st.number_input(
                "Vessel setup cost ($)",
                min_value=0.0, value=200.0, help=r"$C_S$"
            )
            C2 = st.number_input(
                "Cleaning 2 cost ($)",
                min_value=0.0, value=500.0, help=r"$C_2$"
            )
            CP = st.number_input(
                "Production loss cost ($/h)",
                min_value=0.0, value=3.51, help=r"$C_P$"
            )
        
        with col2:
            Kappa2 = st.number_input(
                "Feed water quality parameter 2",
                min_value=0.0, value=0.0025, help=r"$\kappa_2$"
            )
            Alpha = st.number_input(
                "Biofouling-wear distribution parameter",
                min_value=0.0, value=0.65, help=r"$\alpha$"
            )
            R = st.number_input(
                "System recovery",
                min_value=0.0, value=0.998, help=r"$R$"
            )
            C1 = st.number_input(
                "Cleaning 1 cost ($)",
                min_value=0.0, value=400.0, help=r"$C_1$"
            )
            CR = st.number_input(
                "Membrane replacement cost ($)",
                min_value=0.0, value=400.0, help=r"$C_R$"
            )
            DD = st.number_input(
                "Membrane access downtime (h)",
                min_value=0.0, value=0.25, help=r"$d_D$"
            )
        
        with col3:
            CD = st.number_input(
                "Membrane removal cost ($/membrane)",
                min_value=0.0, value=100.0, help=r"$C_D$"
            )
            DR = st.number_input(
                "Preventive replacement downtime (h)",
                min_value=0.0, value=3.0, help=r"$d_R$"
            )
            DF = st.number_input(
                "Corrective replacement downtime (h)",
                min_value=0.0, value=6.0, help=r"$d_F$"
            )
            D1 = st.number_input(
                "Cleaning 1 downtime (h)",
                min_value=0.0, value=1.0, help=r"$d_1$"
            )
            D2 = st.number_input(
                "Cleaning 2 downtime (h)",
                min_value=0.0, value=2.0, help=r"$d_2$"
            )
        
        
        N=int(st.text_input("Insert the number of membranes (N)", value=8))
        FailureThreshold=st.number_input("Insert the failure threshold", min_value = 0.0, value = 3.0, help=r"$L$")
        Preventive=st.number_input("Insert the preventive threshold", min_value = 0.0, value = 2.99, help=r"$\theta_P$")
        Opportunistic=st.number_input("Insert the opportunistic threshold", min_value = 0.0, value = 2.80, help=r"$\theta_O$")
        Cleaning1=st.number_input("Insert the cleaning 1 threshold", min_value = 0.0, value = 10.00, help=r"$\theta_{C_1}$")
        Cleaning2=st.number_input("Insert the cleaning 2 threshold", min_value = 0.0, value = 13.00, help=r"$\theta_{C_2}$")
        
        botao = st.button("Get cost")
        if botao:
            
            
    if choice == menu[1]:
        st.header(menu[1])
        st.write("<h6 style='text-align: justify; color: Blue Jay;'>This app is dedicated to computing the cost for the maintenance policy proposed for reverse-osmosis systems.</h6>", unsafe_allow_html=True)
        st.write("<h6 style='text-align: justify; color: Blue Jay;'>The app computes the cost for a specific solution, setting the thresholds for preventive, opportunistic, cleaning 1 and cleaning 2 actions.</h6>", unsafe_allow_html=True)
        st.write("<h6 style='text-align: justify; color: Blue Jay;'>For further questions or information on finding the optimal solution, please contact one of the email addresses below.</h6>", unsafe_allow_html=True)
        
        st.write('''

        v.h.r.lima@random.org.br
        
        c.a.v.cavalcante@random.org.br
        
        ''' .format(chr(948), chr(948), chr(948), chr(948), chr(948)))       
    if choice==menu[2]:
        st.header(menu[2])
        
        st.write('''The Research Group on Risk and Decision Analysis in Operations and Maintenance was created in 2012 
                 in order to bring together different researchers who work in the following areas: risk, maintenance a
                 nd operation modelling. Learn more about it through our website.''')
        st.markdown('[Click here to be redirected to our website](https://sites.ufpe.br/random/#page-top)',False)        
if __name__ == "__main__":
    main()
