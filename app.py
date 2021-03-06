from flask import Flask, jsonify, request
import numpy as np
import joblib
from tensorflow.keras.models import load_model
# https://www.tutorialspoint.com/flask
import flask
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/index')
def index():
    return flask.render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    model = load_model('encoder_full.h5')
    threshold = joblib.load('encoder_threshold.pkl')
    ohe = joblib.load('one_hot_encoder.pkl')
    mm = joblib.load('mm_scaler.pkl')
    to_predict_list = request.form.to_dict()
   
    
    
    cat_features = []
    for ele in ['protocol_type'	,'service'	,'flag']:
        cat_features.append(to_predict_list[ele])
    ohe_data = ohe.transform(np.array(cat_features).reshape(1,-1))
    
    
    bin_features = []
    for ele in ['land','logged_in','root_shell','is_host_login','is_guest_login']:
        bin_features.append(int(to_predict_list[ele]))
    
    num_features = []
    for ele in ['duration', 'src_bytes', 'dst_bytes', 'wrong_fragment', 'urgent', 'hot','num_failed_logins', 'num_compromised', 'su_attempted', 'num_root','num_file_creations', 'num_shells', 'num_access_files', 'count','srv_count', 'serror_rate', 'srv_serror_rate', 'rerror_rate','srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate','srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count','dst_host_same_srv_rate', 'dst_host_diff_srv_rate','dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate','dst_host_serror_rate', 'dst_host_srv_serror_rate','dst_host_rerror_rate', 'dst_host_srv_rerror_rate']:
        try:
            num_features.append(float(to_predict_list[ele]))
        except:
            return "Warning!! Enter only numerical values"
    num_features = mm.transform(np.array(num_features).reshape(1,-1)).reshape(1,-1)[0]
    query = np.concatenate((ohe_data.toarray()[0],np.array(bin_features),np.array(num_features)))
    
    
    
       
    prediction = model.predict(query.reshape(1,-1))
    diff_arr = prediction - query.reshape(1,-1)
    sqr_error_arr = np.sum(diff_arr**2,axis=1)/120
    predict_label = np.where(sqr_error_arr > threshold, 1, 0)
 
    if predict_label[0] == 0:
        query_prediction = "Normal"
    else:
        query_prediction = "Anomaly"
    print(query_prediction)
    return jsonify({'prediction': query_prediction})
    


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
