import math
import gurobipy as gp
from gurobipy import GRB, quicksum
from matplotlib.pylab import beta
import matplotlib.pyplot as plt
import numpy as np



def generateData(mean, std_dev, size):
    # Generate data based on normal distribution with mean and standard deviation
    # Only positive values are considered for reliability analysis, so we filter out negative values.
    data = np.random.normal(mean, std_dev, size)
    return data[data > 0]


def PDF_Reliability(t, theta, beta):
    return (beta / theta) * math.pow(t / theta, beta - 1) * math.exp(-math.pow(t / theta, beta))

def CDF_Reliability(t, theta, beta):
    return 1 - math.exp(-math.pow(t / theta, beta))

def estimate_CDF_Reliability(data):
    # Data is a list of time of failure observations.

    n = len(data)
    data = sorted(data)
    transformed = []
    for rank, time in enumerate(data, start=1):
        # Median-rank estimate: F_hat = (i - 0.3) / (n + 0.4).
        cdf = (rank - 0.3) / (n + 0.4)
        transformed.append((
            math.log(time),
            math.log(-math.log1p(-cdf)),
        ))

    mean_x = sum(x for x, _ in transformed) / n
    mean_y = sum(y for _, y in transformed) / n
    variance_x = sum((x - mean_x) ** 2 for x, _ in transformed)
    if variance_x == 0:
        raise ValueError("observation times must not all be equal")

    beta = sum(
        (x - mean_x) * (y - mean_y) for x, y in transformed
    ) / variance_x
    if beta <= 0:
        raise ValueError("estimated beta must be positive")

    # y = beta * log(t) - beta * log(theta).
    theta = math.exp((beta * mean_x - mean_y) / beta)

    # Print Weibull plot (log-log scale)
    plt.figure()
    plt.title("Weibull Plot")
    plt.xlabel("log(Time)")
    plt.ylabel("log(-log(1 - F_hat))")
    plt.scatter([x for x, _ in transformed], [y for _, y in transformed], label="Data Points")
    plt.plot([x for x, _ in transformed], [beta * x - beta *math.log(theta) for x, _ in transformed], color='red', label="Fitted Line")
    plt.legend()
    plt.show()
    return beta, theta

def plotCDF(beta, theta):
    # Range of times per 0.25 years from 0 to 150 years
    T = 100
    t = [i * 0.25 for i in range(T*4)]
    cdf = [CDF_Reliability(time, theta, beta) for time in t]
    plt.plot(t, cdf, label=f'beta={beta}, theta={theta}')
    plt.title("Weibull Distribution")
    plt.xlabel("Time (years)")
    plt.ylabel("Reliability")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    data = generateData(40, 8, 100)
    print(data)
    beta, theta = estimate_CDF_Reliability(data)
    plotCDF(beta, theta)
    print(f"Estimated beta: {beta}, Estimated theta: {theta}")