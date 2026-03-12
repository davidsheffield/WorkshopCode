import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit


def _model(Xdata, calibration, bias, backgear_ratio):
    """
    Predicted RPM as a function of ADC reading and speed range.

    High speed: RPM = calibration * x + bias
    Low speed:  RPM = (calibration / backgear_ratio) * x + (bias / backgear_ratio)
    """
    x, is_high = Xdata
    return np.where(is_high, calibration * x + bias,
                    (calibration / backgear_ratio) * x + (bias / backgear_ratio))


def calibrate():
    """
    Fit calibration, bias, and backgear_ratio to measured ADC/RPM data.

    Reads calibration_measurements.csv and performs a nonlinear least-squares
    fit of _model to the data. Prints and returns the fitted parameters.
    """
    data = pd.read_csv('calibration_measurements.csv')
    adc = data['ADC reading'].values
    is_high = data['High speed'].values.astype(float)
    y = data['Speed [RPM]'].values

    (calibration, bias, backgear_ratio), _ = curve_fit(
        _model, (adc, is_high), y, p0=[3.7, 392.0, 8.8]
    )

    print(f'calibration    = {calibration:.6f}')
    print(f'bias           = {bias:.6f}')
    print(f'backgear_ratio = {backgear_ratio:.6f}')

    return calibration, bias, backgear_ratio


def plot(calibration, bias, backgear_ratio):
    """
    Plot calibration data and fit lines.

    Generates three figures:
      1. ADC reading vs potentiometer mark
      2. Speed (RPM) vs potentiometer mark
      3. Speed (RPM) vs ADC reading, with high and low speed fit lines
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
    x_fit = np.array([data['ADC reading'].min(), data['ADC reading'].max()])
    ax3.plot(x_fit, calibration * x_fit + bias, label='High speed fit')
    ax3.plot(x_fit, (calibration / backgear_ratio) * x_fit + (bias / backgear_ratio), label='Low speed fit')
    ax3.set_xlabel('ADC reading')
    ax3.set_ylabel('Speed [RPM]')
    ax3.legend()
    ax3.tick_params(direction='in', top=True, right=True)

    plt.show()

if __name__ == '__main__':
    calibration, bias, backgear_ratio = calibrate()
    plot(calibration, bias, backgear_ratio)
