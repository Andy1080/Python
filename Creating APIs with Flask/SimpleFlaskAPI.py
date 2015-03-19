from flask import Flask, request, send_file
app = Flask(__name__)

# Example "Hello World".
@app.route("/")
def hello():
    return "Hello World!"

# Example using custom URLs.
@app.route('/user/<username>')
def custom_url(username):
    return """User: {}""".format(username)
  
# Example using parameters.
@app.route('/parameters')  
def passing_parameters():
    name = request.args.get('name')    
    age = request.args.get('age')
    return """Information for {}, aged {}""".format(name,age) 

# Example using non-text output.
@app.route('/image')
def show_image():
    return send_file('network.png', mimetype='image/png')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)