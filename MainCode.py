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
from numba import njit
#######################################################################################
@njit
def Kappat(t, Kappa1, Kappa2, Beta):
    i = 0
    while i < len(BloomData):
        if BloomData[i] > t:
            break
        else:
            i += 1
    return (Kappa2 - Kappa1) * numpy.exp(-Beta * (t - BloomData[i - 1]))

@njit
def DegradationModel(OldDegradation, Kappa, Alpha, Gamma, R, Component):
    if Component < N - 1:
        Sum = 0.0
        for j in range(Component + 1, N):
            Sum += OldDegradation[j]

        DeltaDegradation = (Kappa* Alpha**Component* ((Sum / (N - Component - 1)) ** (R * Gamma)))
    else:
        DeltaDegradation = Kappa * Alpha**Component

    return OldDegradation[Component] + DeltaDegradation

@njit
def DecisionProblem(Degradations,Preventive,Opportunistic,Cleaning1,Cleaning2,Failure):
    Actions = numpy.zeros(N + 2, dtype=numpy.int8)

    # Deciding cleanings
    if sum(Degradations) > Cleaning2:
        Actions[0] = 2
    elif sum(Degradations) > Cleaning1:
        Actions[0] = 1

    # Deciding preventive replacements
    if Failure:
        for i in range(N):
            if Degradations[i] >= FailureThreshold:
                Actions[i + 2] = 1

        for i in range(N):
            if Opportunistic < Degradations[i] < FailureThreshold:
                Actions[i + 2] = 1
    else:
        for i in range(N):
            if Degradations[i] >= Preventive:
                Actions[i + 2] = 1
                break

        for i in range(N):
            if Opportunistic < Degradations[i] < Preventive:
                Actions[i + 2] = 1

    # Deciding swappings
    Actions[1] = 0
    for i in range(N):
        if Actions[i + 2] == 1:
            Actions[1] = i + 1

    return Actions

@njit
def SimulationThresholds(Preventive,Opportunistic,Cleaning1,Cleaning2,FailureThreshold,ConvergenceDays,Kappa1,Kappa2,Beta,Alpha,Gamma,R,CS,C1,C2,CR,CD,CP,DD,DR,DF,D1,D2):
    Cost = 0.0
    Day = 0

    Degradations = numpy.ones(N, dtype=numpy.float64)
    Actions = numpy.zeros(N + 2, dtype=numpy.int8)

    while Day < BloomData[-1] + ConvergenceDays:

        # Testing the preventive threshold
        Break = False
        for i in range(N):
            if Degradations[i] >= Preventive:
                Break = True
                break

        # Decision problem
        if Break:
            Actions = DecisionProblem(
                Degradations, Preventive, Opportunistic,
                Cleaning1, Cleaning2, False
            )
        else:
            Actions[:] = 0

        Downtime = 0.0
        NewDegradations = Degradations.copy()

        # Cleaning decisions
        if Actions[0] == 1:
            Cost += C1
            Downtime += D1

            for i in range(N):
                NewDegradations[i] = (
                    (1 - delta0) * NewDegradations[i] + delta0
                )

        elif Actions[0] == 2:
            Cost += C2
            Downtime += D2

            for i in range(N):
                NewDegradations[i] = (
                    (1 - delta1) * NewDegradations[i] + delta1
                )

        # Preventive replacements
        Setup = False
        for i in range(2, len(Actions)):
            if Actions[i] == 1:
                Setup = True
                NewDegradations[i - 2] = 1.0
                Cost += CR

        if Setup:
            Downtime += DR

        Cost += Actions[1] * CD
        Downtime += Actions[1] * DD

        if Actions[1] > 0:
            Setup = True
            NewDegradations[:Actions[1]] = numpy.sort(
                NewDegradations[:Actions[1]]
            )

        Cost += CS * Setup
        Cost += Downtime * CP

        # Computing new degradations
        Kappa = Kappat(Day, Kappa1, Kappa2, Beta)

        for i in range(N):
            Degradations[i] = DegradationModel(
                NewDegradations, Kappa, Alpha, Gamma, R, i
            )

        # Checking failure
        Failure = False
        for i in range(N):
            if Degradations[i] > FailureThreshold:
                Failure = True
                break

        if Failure:
            # Corrective opportunity
            Cost += CS
            Cost += DF * CP

            Actions = DecisionProblem(
                Degradations, Preventive, Opportunistic,
                Cleaning1, Cleaning2, True
            )

            if Actions[0] == 1:
                Cost += C1
                Cost += D1 * CP

                for i in range(N):
                    Degradations[i] = (
                        (1 - delta0) * Degradations[i] + delta0
                    )

            elif Actions[0] == 2:
                Cost += C2
                Cost += D2 * CP

                for i in range(N):
                    Degradations[i] = (
                        (1 - delta1) * Degradations[i] + delta1
                    )

            for i in range(2, len(Actions)):
                if Actions[i] == 1:
                    Cost += CR
                    Degradations[i - 2] = 1.0
                    Actions[1] = max(Actions[1], i - 1)

            Cost += Actions[1] * (CD + DD * CP)

            Degradations[:Actions[1]] = numpy.sort(
                Degradations[:Actions[1]]
            )

        Day += 1

    return Cost

def Metrics(Preventive,Opportunistic,Cleaning1,Cleaning2,FailureThreshold,ConvergenceDays,Kappa1,Kappa2,Beta,Alpha,Gamma,R,CS,C1,C2,CR,CD,CP,DD,DR,DF,D1,D2):
    Cleanings1 = 0
    Cleanings2 = 0
    PreventiveActivations = 0

    Preventives = [0] * N
    Correctives = [0] * N
    Breaks = []

    OvertimeDegradations = [[1.0] for _ in range(N)]

    Day = 0
    Degradations = numpy.ones(N, dtype=numpy.float64)
    Actions = numpy.zeros(N + 2, dtype=numpy.int8)

    while Day < BloomData[-1] + ConvergenceDays:

        # Testing the preventive threshold
        Break = False
        for i in range(N):
            if Degradations[i] >= Preventive:
                Break = True
                PreventiveActivations += 1
                break

        # Decision problem
        if Break:
            Breaks.append(Day)
            Actions = DecisionProblem(
                Degradations, Preventive, Opportunistic,
                Cleaning1, Cleaning2, False
            )
        else:
            Actions[:] = 0

        NewDegradations = Degradations.copy()

        # Cleaning decisions
        if Actions[0] == 1:
            Cleanings1 += 1
            for i in range(N):
                NewDegradations[i] = (
                    (1 - delta0) * NewDegradations[i] + delta0
                )

        elif Actions[0] == 2:
            Cleanings2 += 1
            for i in range(N):
                NewDegradations[i] = (
                    (1 - delta1) * NewDegradations[i] + delta1
                )

        # Preventive replacements
        for i in range(2, len(Actions)):
            if Actions[i] == 1:
                Preventives[i - 2] += 1
                NewDegradations[i - 2] = 1.0

        if Actions[1] > 0:
            NewDegradations[:Actions[1]] = numpy.sort(
                NewDegradations[:Actions[1]]
            )

        # Computing new degradations
        Kappa = Kappat(Day, Kappa1, Kappa2, Beta)

        for i in range(N):
            Degradations[i] = DegradationModel(
                NewDegradations, Kappa, Alpha, Gamma, R, i
            )

        # Checking failure
        Failure = False
        CorrectiveComp = -1

        for i in range(N):
            if Degradations[i] > FailureThreshold:
                Correctives[i] += 1
                Failure = True
                CorrectiveComp = i
                break

        if Failure:
            Breaks.append(Day)

            Actions = DecisionProblem(
                Degradations, Preventive, Opportunistic,
                Cleaning1, Cleaning2, True
            )

            if Actions[0] == 1:
                Cleanings1 += 1
                for i in range(N):
                    Degradations[i] = (
                        (1 - delta0) * Degradations[i] + delta0
                    )

            elif Actions[0] == 2:
                Cleanings2 += 1
                for i in range(N):
                    Degradations[i] = (
                        (1 - delta1) * Degradations[i] + delta1
                    )

            for i in range(2, len(Actions)):
                if Actions[i] == 1:
                    if i - 2 != CorrectiveComp:
                        Preventives[i - 2] += 1

                    Degradations[i - 2] = 1.0

            Degradations[:Actions[1]] = numpy.sort(
                Degradations[:Actions[1]]
            )

        Day += 1

        for i in range(N):
            OvertimeDegradations[i].append(Degradations[i])

    # Plotting degradation trajectories
    for Line in OvertimeDegradations:
        plt.plot(Line, linewidth=0.75)

    plt.vlines(
        Breaks,
        ymin=1.0 - 0.01,
        ymax=1.0 + 0.01,
        color="black",
        linewidth=1.25,
        label="Maint. Break"
    )

    plt.xlabel("Day")
    plt.ylabel("Degradation")
    plt.grid(True)
    plt.legend(
        [f"{i + 1}" for i in range(N)],
        loc="upper left",
        fontsize=6
    )
    plt.show()

    print("# of Cleanings 1:", Cleanings1)
    print("# of Cleanings 2:", Cleanings2)
    print("# of Prev. Activations:", PreventiveActivations)

    for i in range(N):
        print(
            f"# of preventives and correctives in {i + 1}:",
            Preventives[i],
            Correctives[i]
        )

    return (
        len(Breaks),
        Cleanings1,
        Cleanings2,
        sum(Preventives),
        sum(Correctives)
    )

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
        col1, col2 = st.columns(2)

        with col1:
            Kappa1 = st.number_input("Feed water quality parameter 1", min_value=0.0, value=0.0014, help=r"$\kappa_1$")
            Kappa2 = st.number_input("Feed water quality parameter 2", min_value=0.0, value=0.0025, help=r"$\kappa_2$")
            Beta = st.number_input("Algae bloom dissipation rate", min_value=0.0, value=0.026, help=r"$\beta$")
            Alpha = st.number_input("Biofouling-wear distribution parameter", min_value=0.0, value=0.65, help=r"$\alpha$")
            Gamma = st.number_input("Stochastic dependence strength", min_value=0.0, value=0.73, help=r"$\gamma$")
            R = st.number_input("System recovery", min_value=0.0, value=0.998, help=r"$R$")
            CS = st.number_input("Vessel setup cost ($)", min_value=0.0, value=200.0, help=r"$C_S$")
            C1 = st.number_input("Cleaning 1 cost ($)", min_value=0.0, value=400.0, help=r"$C_1$")
            C2 = st.number_input("Cleaning 2 cost ($)", min_value=0.0, value=500.0, help=r"$C_2$")
        
        with col2:
            CR = st.number_input("Membrane replacement cost ($)", min_value=0.0, value=400.0, help=r"$C_R$")
            CD = st.number_input("Membrane removal cost ($/membrane)", min_value=0.0, value=100.0, help=r"$C_D$")
            CP = st.number_input("Production loss cost ($/h)", min_value=0.0, value=3.51, help=r"$C_P$")
            DD = st.number_input("Membrane access downtime (h)", min_value=0.0, value=0.25, help=r"$d_D$")
            DR = st.number_input("Preventive replacement downtime (h)", min_value=0.0, value=3.0, help=r"$d_R$")
            DF = st.number_input("Corrective replacement downtime (h)", min_value=0.0, value=6.0, help=r"$d_F$")
            D1 = st.number_input("Cleaning 1 downtime (h)", min_value=0.0, value=1.0, help=r"$d_1$")
            D2 = st.number_input("Cleaning 2 downtime (h)", min_value=0.0, value=2.0, help=r"$d_2$")
        
        st.subheader("Insert the variable values below:")
        N=int(st.text_input("Insert the number of membranes (N)", value=8))
        FailureThreshold=st.number_input("Insert the failure threshold", min_value = 0.0, value = 3.0, help=r"$L$")
        Preventive=st.number_input("Insert the preventive threshold", min_value = 0.0, value = 2.99, help=r"$\theta_P$")
        Opportunistic=st.number_input("Insert the opportunistic threshold", min_value = 0.0, value = 2.80, help=r"$\theta_O$")
        Cleaning1=st.number_input("Insert the cleaning 1 threshold", min_value = 0.0, value = 10.00, help=r"$\theta_{C_1}$")
        Cleaning2=st.number_input("Insert the cleaning 2 threshold", min_value = 0.0, value = 13.00, help=r"$\theta_{C_2}$")
        
        botao = st.button("Get cost")
        if botao:
            ConvergenceDays=-1
            Cost = SimulationThresholds(Preventive,Opportunistic,Cleaning1,Cleaning2,FailureThreshold,ConvergenceDays,Kappa1,Kappa2,Beta,Alpha,Gamma,R,CS,C1,C2,CR,CD,CP,DD,DR,DF,D1,D2)
            Results = Metrics(Preventive,Opportunistic,Cleaning1,Cleaning2,FailureThreshold,ConvergenceDays,Kappa1,Kappa2,Beta,Alpha,Gamma,R,CS,C1,C2,CR,CD,CP,DD,DR,DF,D1,D2)
            
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
