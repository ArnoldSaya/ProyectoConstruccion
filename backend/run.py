from app import create_app
app.config["PREFERRED_URL_SCHEME"] = "https"
app = create_app()

if __name__ == '__main__':
    # use_reloader=False evita el bug de WinError 10038 del hilo watchdog
    # de Flask en Windows al recargar archivos. En Linux puedes ponerlo True.
    app.run(debug=True, port=5000, use_reloader=False)
