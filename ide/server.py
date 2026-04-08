"""
Servidor IDE para CCODE.
Ejecuta código CCODE y maneja I/O interactivo via WebSockets.
"""
import sys
import os
import threading
import queue
import io

from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit

_BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_BASE, '..', 'src', 'lexer'))
sys.path.insert(0, os.path.join(_BASE, '..', 'src', 'parser'))

from tokenizer import tokenizar_codigo, ErrorLexico
from parser import parsear_codigo, ErrorSintactico
from interprete import Interprete, ErrorEjecucion

STATIC = os.path.join(_BASE, 'frontend', 'dist')

app = Flask(__name__, static_folder=STATIC, static_url_path='')
app.config['SECRET_KEY'] = 'ccode-ide-secret'
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='threading')

# sid -> queue para input interactivo
_input_queues: dict[str, queue.Queue] = {}


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    full = os.path.join(STATIC, path)
    if path and os.path.exists(full):
        return send_from_directory(STATIC, path)
    return send_from_directory(STATIC, 'index.html')


@socketio.on('connect')
def on_connect():
    emit('connected', {'msg': 'Conectado al servidor CCODE'})


@socketio.on('disconnect')
def on_disconnect():
    from flask import request
    _input_queues.pop(request.sid, None)


@socketio.on('ejecutar')
def on_ejecutar(data):
    from flask import request
    sid = request.sid
    codigo = data.get('codigo', '')

    q = queue.Queue()
    _input_queues[sid] = q

    def run():
        # --- stdout/stderr/stdin thread-local para no mezclar entre ejecuciones ---
        import threading
        _local = threading.local()

        class SocketWriter(io.TextIOBase):
            def write(self, s):
                if s:
                    socketio.emit('output', {'text': s, 'stream': 'stdout'}, to=sid)
                return len(s)
            def flush(self): pass

        class SocketErrWriter(io.TextIOBase):
            def write(self, s):
                if s:
                    socketio.emit('output', {'text': s, 'stream': 'stderr'}, to=sid)
                return len(s)
            def flush(self): pass

        class SocketReader(io.TextIOBase):
            def readline(self):
                socketio.emit('input_request', {}, to=sid)
                try:
                    val = q.get(timeout=60)
                except queue.Empty:
                    val = ''
                socketio.emit('output', {'text': val + '\n', 'stream': 'stdin'}, to=sid)
                return val + '\n'

        old_out, old_err, old_in = sys.stdout, sys.stderr, sys.stdin
        sys.stdout = SocketWriter()
        sys.stderr = SocketErrWriter()
        sys.stdin  = SocketReader()

        try:
            tokens = tokenizar_codigo(codigo)
            ast    = parsear_codigo(tokens)
            interp = Interprete()
            interp.ejecutar(ast)
            socketio.emit('done', {'exitCode': 0}, to=sid)
        except ErrorLexico as e:
            socketio.emit('output', {'text': str(e) + '\n', 'stream': 'stderr'}, to=sid)
            socketio.emit('done', {'exitCode': 1}, to=sid)
        except ErrorSintactico as e:
            socketio.emit('output', {'text': str(e) + '\n', 'stream': 'stderr'}, to=sid)
            socketio.emit('done', {'exitCode': 1}, to=sid)
        except ErrorEjecucion as e:
            socketio.emit('output', {'text': f'[Error de ejecucion] {e}\n', 'stream': 'stderr'}, to=sid)
            socketio.emit('done', {'exitCode': 1}, to=sid)
        except Exception as e:
            socketio.emit('output', {'text': f'[Error interno] {e}\n', 'stream': 'stderr'}, to=sid)
            socketio.emit('done', {'exitCode': 1}, to=sid)
        finally:
            sys.stdout, sys.stderr, sys.stdin = old_out, old_err, old_in
            _input_queues.pop(sid, None)

    t = threading.Thread(target=run, daemon=True)
    t.start()


@socketio.on('input_response')
def on_input_response(data):
    from flask import request
    q = _input_queues.get(request.sid)
    if q:
        q.put(data.get('value', ''))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f'CCODE IDE corriendo en http://localhost:{port}')
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
