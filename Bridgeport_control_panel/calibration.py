import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def calibrate():
    """
    Calculate the control panel's calibration, bias, and BACKGEAR_RATIO.
    """
    data = pd.read_csv('calibration_measurements.csv')

    # Build feature matrix: high speed rows use [ADC, 0], low speed rows use [0, ADC]
    adc = data['ADC reading'].values
    is_high = data['High speed'].values
    X = np.column_stack([adc * is_high, adc * (1 - is_high)])
    y = data['Speed [RPM]'].values

    model = LinearRegression(fit_intercept=True)
    model.fit(X, y)

    calibration = model.coef_[0]
    bias = model.intercept_
    backgear_ratio = model.coef_[0] / model.coef_[1]

    print(f'calibration   = {calibration:.6f}')
    print(f'bias          = {bias:.6f}')
    print(f'backgear_ratio = {backgear_ratio:.6f}')


def plot():
    """
    Plot the calibration data
    """

    data = pd.read_csv('calibration_measurements.csv')
    high = data[data['High speed'] == 1]
    low = data[data['High speed'] == 0]
    has_mark = data['Potentiometer mark'].notnull()

    # Figure 1: ADC reading vs Potentiometer mark
    fig1, ax1 = plt.subplots()
    ax1.scatter(high.loc[has_mark, 'Potentiometer mark'],
                high.loc[has_mark, 'ADC reading'],
                label='High speed')
    ax1.scatter(low.loc[has_mark, 'Potentiometer mark'],
                low.loc[has_mark, 'ADC reading'],
                label='Low speed')
    ax1.set_xlabel('Potentiometer mark')
    ax1.set_ylabel('ADC reading')
    ax1.legend()
    ax1.tick_params(direction='in', top=True, right=True)

    # Figure 2: Speed [RPM] vs Potentiometer mark
    fig2, ax2 = plt.subplots()
    ax2.scatter(high.loc[has_mark, 'Potentiometer mark'],
                high.loc[has_mark, 'Speed [RPM]'],
                label='High speed')
    ax2.scatter(low.loc[has_mark, 'Potentiometer mark'],
                low.loc[has_mark, 'Speed [RPM]'],
                label='Low speed')
    ax2.set_xlabel('Potentiometer mark')
    ax2.set_ylabel('Speed [RPM]')
    ax2.legend()
    ax2.tick_params(direction='in', top=True, right=True)

    # Figure 3: Speed [RPM] vs ADC reading
    fig3, ax3 = plt.subplots()
    ax3.scatter(high['ADC reading'], high['Speed [RPM]'], label='High speed')
    ax3.scatter(low['ADC reading'], low['Speed [RPM]'], label='Low speed')
    ax3.set_xlabel('ADC reading')
    ax3.set_ylabel('Speed [RPM]')
    ax3.legend()
    ax3.tick_params(direction='in', top=True, right=True)

    plt.show()

if __name__ == '__main__':
    calibrate()
    # plot()
