from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def conectar():
    return sqlite3.connect("clinica.db")

@app.route("/")
def index():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM clientes")
    total_clientes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM servicos")
    total_servicos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM agendamentos")
    total_agendamentos = cursor.fetchone()[0]

    cursor.execute("""
    SELECT servicos.valor 
    FROM agendamentos
    JOIN servicos ON agendamentos.servico = servicos.nome
    """)

    faturamento = sum([float(str(row[0]).replace(",", ".") or 0) for row in cursor.fetchall()])

    cursor.execute("SELECT cliente, servico, data, hora FROM agendamentos")
    agendamentos = cursor.fetchall()

    conn.close()

    return render_template(
        "index.html",
        agendamentos=agendamentos,
        total_clientes=total_clientes,
        total_servicos=total_servicos,
        total_agendamentos=total_agendamentos,
        faturamento=faturamento
    )

@app.route("/clientes", methods=["GET","POST"])
def clientes():

    if request.method == "POST":

        nome = request.form["nome"]
        telefone = request.form["telefone"]
        email = request.form["email"]

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO clientes (nome, telefone, email) VALUES (?,?,?)",
            (nome, telefone, email)
        )

        conn.commit()
        conn.close()

        return redirect("/clientes")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()

    conn.close()

    return render_template("clientes.html", clientes=clientes)


@app.route("/servicos", methods=["GET","POST"])
def servicos():

    if request.method == "POST":
        nome = request.form["nome"]
        valor = request.form["valor"].replace(",", ".")
        valor = float(valor)

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO servicos (nome, valor) VALUES (?,?)",
            (nome, valor)
        )

        conn.commit()
        conn.close()

        return redirect("/servicos")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM servicos")
    servicos = cursor.fetchall()

    conn.close()

    return render_template("servicos.html", servicos=servicos)


@app.route("/agendar", methods=["GET","POST"])
def agendar():

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":

        cliente = request.form["cliente"]
        servico = request.form["servico"]
        data = request.form["data"]
        hora = request.form["hora"]

        cursor.execute(
            "INSERT INTO agendamentos (cliente, servico, data, hora) VALUES (?,?,?,?)",
            (cliente, servico, data, hora)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    cursor.execute("SELECT nome FROM clientes")
    clientes = cursor.fetchall()

    cursor.execute("SELECT nome FROM servicos")
    servicos = cursor.fetchall()

    conn.close()

    return render_template("agendar.html", clientes=clientes, servicos=servicos)


if __name__ == "__main__":
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        telefone TEXT,
        email TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS servicos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        valor REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agendamentos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente TEXT,
        servico TEXT,
        data TEXT,
        hora TEXT
    )
    """)

    conn.commit()
    conn.close()

    app.run(debug=True)

@app.route("/excluir_cliente/<int:id>")
def excluir_cliente(id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM clientes WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    return redirect("/clientes")

@app.route("/editar_cliente/<int:id>", methods=["GET","POST"])
def editar_cliente(id):

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":

        nome = request.form["nome"]
        telefone = request.form["telefone"]
        email = request.form["email"]

        cursor.execute("""
        UPDATE clientes
        SET nome=?, telefone=?, email=?
        WHERE id=?
        """,(nome,telefone,email,id))

        conn.commit()
        conn.close()

        return redirect("/clientes")

    cursor.execute("SELECT * FROM clientes WHERE id=?", (id,))
    cliente = cursor.fetchone()

    conn.close()

    return render_template("editar_cliente.html", cliente=cliente)

@app.route("/excluir_servico/<int:id>")
def excluir_servico(id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM servicos WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/servicos")

@app.route("/excluir_agendamento/<int:id>")
def excluir_agendamento(id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM agendamentos WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/")