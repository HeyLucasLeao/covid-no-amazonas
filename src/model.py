from lightgbm import LGBMRegressor
from sktime.forecasting.model_selection import ExpandingWindowSplitter
from sktime.forecasting.model_evaluation import evaluate
from sktime.forecasting.compose import make_reduction
import numpy as np
import pandas as pd
from src.data import tendencia_de_novos_casos, total_de_casos_amazonas

def treinando_e_prevendo():
    fh = np.arange(1, 14 + 1)
    y = pd.Series(data=tendencia_de_novos_casos.values, index=total_de_casos_amazonas.date)
    y.index.freq = 'D'
    model = LGBMRegressor(random_state=4,
            learning_rate = 0.04591301953670739, 
            num_leaves = 45, 
            min_child_samples = 1, 
            subsample = 0.05,
            colsample_bytree = 0.9828905761860228,
            subsample_freq=1,
            n_estimators=685)
            
    reg = make_reduction(estimator=model, window_length=14)
    cv = ExpandingWindowSplitter(initial_window=60)
    cross_val = evaluate(forecaster=reg, y=y, cv=cv, strategy="refit", return_data=True)
    smape = (cross_val['test_MeanAbsolutePercentageError'].mean() * 100).round(2)
    smape = str(smape)
    smape = smape.replace('.', ',')
    reg.fit(y)
    y_pred = pd.DataFrame(reg.predict(fh).round())
    y_pred.reset_index(inplace=True)
    return y_pred, smape

