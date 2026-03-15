import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, LogLocator
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

    y_pred = _model((adc, is_high), calibration, bias, backgear_ratio)
    chi2 = np.sum((y - y_pred)**2 / y_pred)
    dof = len(y) - 3  # 3 fitted parameters

    print(f'calibration    = {calibration:.6f}')
    print(f'bias           = {bias:.6f}')
    print(f'backgear_ratio = {backgear_ratio:.6f}')
    print(f'chi2 / dof     = {chi2/dof:.4f}')

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
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 1200)
    ax1.legend(loc='upper left')
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
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 4500)
    ax2.legend()
    ax2.tick_params(direction='in', top=True, right=True)

    # Figure 3: Speed [RPM] vs ADC reading, with residuals panel
    fig3, (ax3, ax3r) = plt.subplots(
        2, 1, sharex=True,
        gridspec_kw={'height_ratios': [3, 1]},
        figsize=(6.4, 5.5),
    )
    fig3.subplots_adjust(hspace=0.05)
    ax3.scatter(high['ADC reading'], high['Speed [RPM]'], label='High speed')
    ax3.scatter(low['ADC reading'], low['Speed [RPM]'], label='Low speed')
    x_fit = np.array([data['ADC reading'].min(), data['ADC reading'].max()])
    ax3.plot(x_fit, calibration * x_fit + bias, label='High speed fit')
    ax3.plot(x_fit, (calibration / backgear_ratio) * x_fit + (bias / backgear_ratio), label='Low speed fit')
    ax3.set_ylabel('Speed [RPM]')
    ax3.set_xlim(0, 1023)
    ax3.set_ylim(0, 4500)
    ax3.legend()
    ax3.tick_params(direction='in', top=True, right=True)

    high_pred = _model(
        (high['ADC reading'].values, np.ones(len(high))),
        calibration, bias, backgear_ratio,
    )
    low_pred = _model(
        (low['ADC reading'].values, np.zeros(len(low))),
        calibration, bias, backgear_ratio,
    )
    high_resid = (high['Speed [RPM]'].values - high_pred) / high_pred
    low_resid = (low['Speed [RPM]'].values - low_pred) / low_pred
    ax3r.axhline(0, color='k', linewidth=0.8, linestyle='--')
    ax3r.scatter(high['ADC reading'], high_resid)
    ax3r.scatter(low['ADC reading'], low_resid)
    ax3r.set_xlabel('ADC reading')
    ax3r.set_ylabel('Residual / expected')
    ax3r.set_xlim(0, 1023)
    ax3r.set_ylim(-0.06, 0.06)
    ax3r.tick_params(direction='in', top=True, right=True)

    plt.show()

def plot_check_calibration():
    """
    Plot measured vs nominal speed from the check calibration dataset.

    Reads calibration_measurements_check_calibration.csv and plots Measured
    speed [RPM] vs Nominal speed [RPM] for high and low speed ranges, with
    a y = x reference line.
    """
    data = pd.read_csv('calibration_measurements_check_calibration.csv')
    high = data[data['High speed'] == 1]
    low  = data[data['High speed'] == 0]

    fig, (ax, axr) = plt.subplots(
        2, 1, sharex=True,
        gridspec_kw={'height_ratios': [3, 1]},
        figsize=(6.4, 5.5),
    )
    fig.subplots_adjust(hspace=0.05, top=0.93, right=0.93)
    lim = 4500 # data['Nominal speed [RPM]'].max() * 1.1
    lo  = 50 # data['Nominal speed [RPM]'].min() * 0.9
    ax.plot([lo, lim], [lo, lim], 'k--', linewidth=0.8)
    ax.scatter(high['Nominal speed [RPM]'], high['Measured speed [RPM]'], label='High speed')
    ax.scatter(low['Nominal speed [RPM]'],  low['Measured speed [RPM]'],  label='Low speed')

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.xaxis.set_major_locator(LogLocator(subs=[1, 2, 3, 5]))
    ax.yaxis.set_major_locator(LogLocator(subs=[1, 2, 3, 5]))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%g'))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%g'))
    ax.set_ylabel('Measured speed [RPM]')
    ax.set_xlim(lo, lim)
    ax.set_ylim(lo, lim)
    ax.legend()
    ax.tick_params(direction='in', top=True, right=True)

    high_resid = (high['Measured speed [RPM]'].values - high['Nominal speed [RPM]'].values) / high['Nominal speed [RPM]'].values
    low_resid  = (low['Measured speed [RPM]'].values  - low['Nominal speed [RPM]'].values)  / low['Nominal speed [RPM]'].values
    axr.axhline(0, color='k', linewidth=0.8, linestyle='--')
    axr.scatter(high['Nominal speed [RPM]'], high_resid)
    axr.scatter(low['Nominal speed [RPM]'],  low_resid)
    axr.set_xlabel('Nominal speed [RPM]')
    axr.set_ylabel('Residual / expected')
    axr.set_xlim(lo, lim)
    axr.tick_params(direction='in', top=True, right=True)

    # --- Second figure: compare all calibration dataset ---
    CAL1_CALIBRATION = 3.700423
    CAL1_BIAS        = 391.732124
    CAL1_BACKGEAR    = 8.858924

    data1 = pd.read_csv('calibration_measurements.csv')
    high1 = data1[data1['High speed'] == 1]
    low1  = data1[data1['High speed'] == 0]

    cal1_high_nominal = CAL1_CALIBRATION * high1['ADC reading'] + CAL1_BIAS
    cal1_low_nominal  = (CAL1_CALIBRATION / CAL1_BACKGEAR) * low1['ADC reading'] + (CAL1_BIAS / CAL1_BACKGEAR)

    fig2, (ax2, ax2r) = plt.subplots(
        2, 1, sharex=True,
        gridspec_kw={'height_ratios': [3, 1]},
        figsize=(6.4, 5.5),
    )
    fig2.subplots_adjust(hspace=0.05, top=0.93, right=0.93)
    ax2.plot([lo, lim], [lo, lim], 'k--', linewidth=0.8)
    ax2.scatter(high['Nominal speed [RPM]'], high['Measured speed [RPM]'], label='Check high speed')
    ax2.scatter(low['Nominal speed [RPM]'],  low['Measured speed [RPM]'],  label='Check low speed')
    ax2.scatter(cal1_high_nominal, high1['Speed [RPM]'], label='Original high speed')
    ax2.scatter(cal1_low_nominal,  low1['Speed [RPM]'],  label='Original low speed')

    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.xaxis.set_major_locator(LogLocator(subs=[1, 2, 3, 5]))
    ax2.yaxis.set_major_locator(LogLocator(subs=[1, 2, 3, 5]))
    ax2.xaxis.set_major_formatter(FormatStrFormatter('%g'))
    ax2.yaxis.set_major_formatter(FormatStrFormatter('%g'))
    ax2.set_ylabel('Measured speed [RPM]')
    ax2.set_xlim(lo, lim)
    ax2.set_ylim(lo, lim)
    ax2.legend()
    ax2.tick_params(direction='in', top=True, right=True)

    cal1_high_resid = (high1['Speed [RPM]'].values - cal1_high_nominal.values) / cal1_high_nominal.values
    cal1_low_resid  = (low1['Speed [RPM]'].values  - cal1_low_nominal.values)  / cal1_low_nominal.values
    ax2r.axhline(0, color='k', linewidth=0.8, linestyle='--')
    ax2r.scatter(high['Nominal speed [RPM]'], high_resid)
    ax2r.scatter(low['Nominal speed [RPM]'],  low_resid)
    ax2r.scatter(cal1_high_nominal, cal1_high_resid)
    ax2r.scatter(cal1_low_nominal,  cal1_low_resid)
    ax2r.set_xlabel('Nominal speed [RPM]')
    ax2r.set_ylabel('Residual / expected')
    ax2r.set_xlim(lo, lim)
    ax2r.tick_params(direction='in', top=True, right=True)

    plt.show()


if __name__ == '__main__':
    calibration, bias, backgear_ratio = calibrate()
    plot(calibration, bias, backgear_ratio)
    plot_check_calibration()
