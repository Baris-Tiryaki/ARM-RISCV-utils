#!/usr/bin/env python3
# pip install flask

from riscv_computer import *

from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='./html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/assemble_api', methods=['POST'])
def assemble_api():
    data = request.data.decode('utf-8')
    return riscv_assemble(data)

@app.route('/disassemble_api', methods=['POST'])
def disassemble_api():
    data = request.data.decode('utf-8')
    return riscv_disassemble(data)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8765, debug=True)

