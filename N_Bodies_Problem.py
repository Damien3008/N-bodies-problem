# =====================================================================================================================================================================================
# Numerical resolution of the N-bodies problem
# =====================================================================================================================================================================================

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Importing Libraries

import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
import time 

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Functions

def import_files(system , time_day , step , t) :
    if system == 'Voyager 2' :
        name = ['Voyager 2','Sun','Earth','Saturn','Jupiter']
    elif system == 'solar system' :
        name = ['Sun','Mercury','Venus','Earth','Mars','Jupiter','Saturn','Uranus','Neptun','Moon','Ceres']
    elif system == 'halley' :
        name = ['Halley comet','Sun']
    elif system == 'Voyager 1' :
        name = ['Voyager 1','Sun','Earth','Saturn','Jupiter']
        
    n = len(name)  
    M = list()  
    T = np.zeros(( 6 * n , len(t)))
    with open(system + '_values.txt','r') as file :
            L = file.readlines()
            for i in range(n):
                M.append(float(L[i]))
            for i in range(n , 6 * n + n , 1) :
                T[i - n , 0] = float(L[i])
    file.close()
    
    return T , M , name , n
    

def Euler_explicite(T , t , pas , M , n , G) :
    for i in range(1,len(t) , 1) :
        T[: , i] = T[: , i - 1] + pas * F(T[: , i - 1] , M , n , G) # Recurrence formula of the explicit Euler method
        
    return T


def Runge_Kutta_2(T , t , pas , M , n , G) :
    for i in range(1 , len(t) , 1) :
        k1 = T[: , i - 1] + pas * F(T[: , i - 1] , M , n , G)
        T[: , i] = T[: , i - 1] + (pas / 2) * (F(T[: , i - 1] , M , n , G) + F(k1 , M , n , G)) # Recurrence formula of the Runge-Kutta method 2
        
    return T


def Runge_Kutta_4( T , t , pas , M , n , G) :
    for i in range(1,len(t) , 1) :
        k1 = pas * F(T[: , i - 1] , M , n , G)
        k2 = pas * F(T[: , i - 1] + (1 / 2) * k1 , M , n , G)
        k3 = pas * F(T[: , i - 1] + (1 / 2) * k2 , M , n , G)
        k4 = pas * F(T[: , i - 1] + k3 , M , n , G)
        T[:,i] = T[: , i - 1]+ (1 / 6) *(k1 + 2 * k2 + 2 * k3 + k4)   # Recurrence formula of the Runge-Kutta method 4
        
    return T

    
def F(Z , M , n , G) :
    K = np.zeros(6 * n) # Creation of an array of 6n rows of zeros that we will come after 
                    # Complete with the Tn + 1 values
    for i in range(0 , n , 1) :
        a = 0
        b = 0
        c = 0
        for j in range(0 , n , 1) :
            if i != j :
                a += (M[j] * (Z[6 * i + 3] - Z[6 * j + 3])) / ((Z[6 * i + 3] - Z[6 * j + 3]) ** 2 + (Z[6 * i + 4] - Z[6 * j + 4]) ** 2 + (Z[6 * i + 5] - Z[6 * j + 5]) ** 2) ** (3 / 2)
                b += (M[j] * (Z[6 * i + 4] - Z[6 * j + 4])) / ((Z[6 * i + 3] - Z[6 * j + 3]) ** 2 + (Z[6 * i + 4] - Z[6 * j + 4]) ** 2 + (Z[6 * i + 5] - Z[6 * j + 5]) ** 2) ** (3 / 2)
                c += (M[j] * (Z[6 * i + 5] - Z[6 * j + 5])) / ((Z[6 * i + 3] - Z[6 * j + 3]) ** 2 + (Z[6 * i + 4] - Z[6 * j + 4]) ** 2 + (Z[6 * i + 5] - Z[6 * j + 5]) ** 2) ** (3 / 2)


        a = - G * a
        b = - G * b
        c = - G * c        
                
                
        K[6 * i] = a
        K[6 * i + 3] = Z[6 * i]
        K[6 * i + 1] = b
        K[6 * i + 4] = Z[6 * i + 1]
        K[6 * i + 2] = c
        K[6 * i + 5] = Z[ 6 * i + 2]
      
    return K


def show_2D(n , T , name , methode) :
    plt.figure("Graphic Representation")
    for i in range(0 , n , 1) :  
        plt.plot(T[6 * i + 3 , :] , T[6 * i + 4 , :] , label = 'trajectory of {}'.format(name[i]))
        plt.plot(T[6 * i + 3 , 0] , T[6 * i + 4 , 0] , 'ko') # we trace the initial positions of each body by a black point
     
    plt.title('Numerical representation for the problem with {} bodies with the method of {}'.format(n , methode))
    plt.xlabel('X (in astronomical units)')
    plt.ylabel('Y (in astronomical units)')     
    plt.grid(linewidth = 0.5)
    plt.axis('equal')
    plt.legend()
    plt.show()


def animation_2D(n , T , name , methode , time_annimation , step):
    show_2D(n , T , name , methode)
    nbr_var = []
    begin = time.time()
    end = time.time()
    
    for i in range(0 , n , 1):
        nbr_var.append(name[i])
        nbr_var[i], = plt.plot([] , [] , 'ko' , linewidth = 5)
        plt.axis('equal')
    for z in range(0 , len(t) , int(len(t) / 100)) :
        if time_annimation >= (end - begin) :
            for i in range(0 , n , 1) :
                nbr_var[i].set_data(T[6 * i + 3 , z] , T[6 * i + 4 , z])
                plt.axis('equal')
                plt.draw()
                plt.pause(step)
            end = time.time()
            

def show_3D(n, T, name, method):
    # Create a 3D plot
    fig = plt.figure("Graphic Representation")
    ax = fig.add_subplot(111, projection='3d')
    
    for i in range(n):
        ax.plot(T[6 * i + 3, :], T[6 * i + 4, :], T[6 * i + 5, :], label=f'Trajectory of {name[i]}')
        ax.scatter(T[6 * i + 3, 0], T[6 * i + 4, 0], T[6 * i + 5, 0], label=f'Start of {name[i]}')

    ax.set_xlabel('X (in astronomical units)')
    ax.set_ylabel('Y (in astronomical units)')
    ax.set_zlabel('Z (in astronomical units)')
    plt.title(f'Numerical representation for the problem with {n} bodies using {method}')
    
    plt.legend()
    plt.show()


def animation_3D(n , T , name , methode , time_annimation , step) :
    show_3D(n , T , name , methode)
    nbr_var = []
    begin = time.time()
    end = time.time()
    for i in range(0 , n , 1) :
        nbr_var.append(name[i])
        nbr_var[i], = plt.plot([] , [] , [] , 'ko' , linewidth = 5)  
    for z in range(0 , len(t) , int(len(t) / 100)) :
        if time_annimation >= (end - begin) :
            for i in range(0 , n , 1) :
                nbr_var[i].set_data(T[6 * i + 3 , z] , T[6 * i + 4 , z])
                nbr_var[i].set_3d_properties(T[6 * i + 5 , z])
                plt.draw()
                plt.pause(step)
            end=time.time()
            

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Constants


G = 1.4872 * 10 ** -34
methode = "Runge_Kutta_4" 
S = ['Voyager 2' , 'solar system' , 'halley' , 'Voyager 1']
systeme = S[1] 
time_day = 10000 # one year
step = 0.1
time_annimation = 20 # seconds


#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Main program

# Time scale
t = np.arange(0 , time_day , step)

# Importing data
T , M , name , n = import_files(systeme , time_day , step , t)

# Explicit Euler Method
#Z = Euler_explicite(T , t , step , M , n , G)

# Runge Kutta 2 Method 
#Z = Runge_Kutta_2(T, t, step , M , n , G)

# Runge Kutta 4 Method 
Z = Runge_Kutta_4(T, t, step, M, n , G)

# Display of the result in 2D
show_2D(n , Z , name , methode)

# Display of the result in 2D with animations
#animation_2D(n , T , name , methode , time_annimation , step)

# Display of the result in 3D
#show_3D(n , Z , name , methode)

# Display of the result in 3D with animations
#animation_3D(n , T , name , methode , time_annimation , step)

    
    
    
    
