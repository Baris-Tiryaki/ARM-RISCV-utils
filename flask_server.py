#!/usr/bin/env python3
# pip install flask

import riscv
import arm

from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='./html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/riscv/assemble_api', methods=['POST'])
def riscv_assemble_api():
    data = request.data.decode('utf-8')
    return riscv.computer.riscv_assemble(data)

@app.route('/riscv/disassemble_api', methods=['POST'])
def riscv_disassemble_api():
    data = request.data.decode('utf-8')
    return riscv.computer.riscv_disassemble(data)



@app.route('/arm/assemble_api', methods=['POST'])
def arm_assemble_api():
    data = request.data.decode('utf-8')
    return arm.computer.assemble(data)

@app.route('/arm/disassemble_api', methods=['POST'])
def arm_disassemble_api():
    data = request.data.decode('utf-8')
    return arm.computer.disassemble(data)



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8765, debug=True)

