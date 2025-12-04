from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def prototype():
    control_frame = {}
    
    if request.method == 'POST':
        # Capture form data into control_frame dict
        control_frame = {
            'event_id': request.form.get('event_id', ''),
            'event_timestamp': request.form.get('event_timestamp', ''),
            'rec_timestamp': request.form.get('rec_timestamp', ''),
            'event_actor': request.form.get('event_actor', ''),
            'event_type': request.form.get('event_type', ''),
            'event_code': request.form.get('event_code', ''),
            'cie_description': request.form.get('cie_description', ''),
            'rel_cred': request.form.get('rel_cred', ''),
            'identified_subjects': request.form.get('identified_subjects', ''),
            'identified_objects': request.form.get('identified_objects', ''),
            'scenario_1hr': request.form.get('scenario_1hr', ''),
            'scenario_6hr': request.form.get('scenario_6hr', ''),
            'scenario_12hr': request.form.get('scenario_12hr', ''),
            'scenario_24hr': request.form.get('scenario_24hr', ''),
            'scenario_prev': request.form.get('scenario_prev', '')
        }
    
    return render_template('prototype.html', cf=control_frame)

if __name__ == '__main__':
    app.run(debug=True, port=5001)