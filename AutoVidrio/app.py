from flask import Flask, render_template, request, jsonify, redirect, url_for, session, Response
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import unicodedata

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "cambia-esta-clave-ultra-secreta"

# --- Usuarios demo ---
USERS = {
    "admin": generate_password_hash("123456"),
    "francisco": generate_password_hash("autovidrio"),
}

# --- Datos mock (en memoria) + IDs ---
CLIENTES = [
    {"id": 1, "razon": "JYC Servicios Integrales Limitada", "rut": "12.345.678-9",
     "region": "Coquimbo", "comuna": "La Serena", "contacto": "Macarena Pizarro",
     "fono": "+56912345678", "cond_pago": "Contado"},
    {"id": 2, "razon": "Fernando Fuentes", "rut": "11.111.111-1",
     "region": "Biobío", "comuna": "Concepción", "contacto": "Fernando Fuentes",
     "fono": "+56982179936", "cond_pago": "30 días"},
    {"id": 3, "razon": "Wilson Arias", "rut": "12.300.000-0",
     "region": "Región Metropolitana", "comuna": "Santiago", "contacto": "Wilson Arias",
     "fono": "+56950236062", "cond_pago": "15 días"},
    {"id": 4, "razon": "Juan Lobos", "rut": "8.571.032-8",
     "region": "Los Lagos", "comuna": "Osorno", "contacto": "Juan Lobos",
     "fono": "+56990207532", "cond_pago": "Crédito"},
    {"id": 5, "razon": "Transportes del Norte Ltda", "rut": "76.543.210-1",
     "region": "Antofagasta", "comuna": "Antofagasta", "contacto": "Claudia Rojas",
     "fono": "+56998765432", "cond_pago": "30 días"},
    {"id": 6, "razon": "Constructora Andes SpA", "rut": "96.123.456-7",
     "region": "O'Higgins", "comuna": "Rancagua", "contacto": "Pedro González",
     "fono": "+56977778888", "cond_pago": "15 días"},
    {"id": 7, "razon": "Agroexportadora Sur Ltda", "rut": "78.234.567-5",
     "region": "Maule", "comuna": "Talca", "contacto": "Gabriela Moya",
     "fono": "+56911112222", "cond_pago": "Contado"},
    {"id": 8, "razon": "Comercial Los Robles", "rut": "67.890.123-4",
     "region": "Araucanía", "comuna": "Temuco", "contacto": "Manuel Herrera",
     "fono": "+56933334444", "cond_pago": "Crédito"},
    {"id": 9, "razon": "Servicios Mineros Altamira", "rut": "88.765.432-1",
     "region": "Atacama", "comuna": "Copiapó", "contacto": "María Jesús Díaz",
     "fono": "+56955556666", "cond_pago": "30 días"},
    {"id": 10, "razon": "Tecnologías del Futuro SpA", "rut": "76.222.333-4",
     "region": "Valparaíso", "comuna": "Viña del Mar", "contacto": "Rodrigo Palma",
     "fono": "+56944445555", "cond_pago": "15 días"},
    {"id": 11, "razon": "Panadería San José", "rut": "12.876.543-2",
     "region": "Ñuble", "comuna": "Chillán", "contacto": "Sofía Campos",
     "fono": "+56999998888", "cond_pago": "Contado"},
    {"id": 12, "razon": "Ferretería El Martillo", "rut": "15.345.678-1",
     "region": "Coquimbo", "comuna": "Ovalle", "contacto": "Hernán Morales",
     "fono": "+56922223333", "cond_pago": "Crédito"},
    {"id": 13, "razon": "Transportes Austral", "rut": "19.456.789-0",
     "region": "Magallanes", "comuna": "Punta Arenas", "contacto": "Camila Reyes",
     "fono": "+56966667777", "cond_pago": "30 días"},
    {"id": 14, "razon": "Frigorífico Sur Ltda", "rut": "18.234.567-2",
     "region": "Aysén", "comuna": "Coyhaique", "contacto": "Alejandro Soto",
     "fono": "+56912121212", "cond_pago": "15 días"},
    {"id": 15, "razon": "Turismo Andino SpA", "rut": "21.987.654-3",
     "region": "Los Ríos", "comuna": "Valdivia", "contacto": "Carolina Méndez",
     "fono": "+56934343434", "cond_pago": "Contado"},
    {"id": 16, "razon": "Editorial Nuevo Milenio", "rut": "13.555.666-7",
     "region": "Región Metropolitana", "comuna": "Providencia", "contacto": "Iván Tapia",
     "fono": "+56978787878", "cond_pago": "30 días"},
    {"id": 17, "razon": "Lácteos del Sur", "rut": "14.444.555-8",
     "region": "Los Lagos", "comuna": "Puerto Montt", "contacto": "Daniela Vergara",
     "fono": "+56956565656", "cond_pago": "Crédito"},
    {"id": 18, "razon": "Clinica San Rafael", "rut": "17.111.222-9",
     "region": "Maule", "comuna": "Curicó", "contacto": "Dr. Esteban Muñoz",
     "fono": "+56989898989", "cond_pago": "15 días"},
    {"id": 19, "razon": "Hotel Bahía Azul", "rut": "20.333.444-5",
     "region": "Valparaíso", "comuna": "Concón", "contacto": "Patricia Lagos",
     "fono": "+56932323232", "cond_pago": "Contado"},
    {"id": 20, "razon": "Inmobiliaria Horizonte", "rut": "77.444.555-6",
     "region": "Región Metropolitana", "comuna": "Las Condes", "contacto": "Felipe Contreras",
     "fono": "+56921212121", "cond_pago": "30 días"},
    {"id": 21, "razon": "Supermercado El Ahorro", "rut": "65.555.666-7",
     "region": "O'Higgins", "comuna": "San Fernando", "contacto": "Beatriz Pérez",
     "fono": "+56910101010", "cond_pago": "15 días"},
    {"id": 22, "razon": "Centro Médico Vida Sana", "rut": "23.333.444-5",
     "region": "Biobío", "comuna": "Los Ángeles", "contacto": "Dr. Juan Ramírez",
     "fono": "+56945454545", "cond_pago": "Crédito"},
    {"id": 23, "razon": "Distribuidora El Faro", "rut": "16.222.333-4",
     "region": "Valparaíso", "comuna": "San Antonio", "contacto": "Tomás Araya",
     "fono": "+56967676767", "cond_pago": "Contado"},
    {"id": 24, "razon": "Restaurante La Picá de Pepe", "rut": "11.222.333-4",
     "region": "Región Metropolitana", "comuna": "Puente Alto", "contacto": "Pepe Martínez",
     "fono": "+56911110000", "cond_pago": "15 días"},
    {"id": 25, "razon": "Escuela Los Alerces", "rut": "10.333.444-5",
     "region": "Araucanía", "comuna": "Angol", "contacto": "Mónica Alarcón",
     "fono": "+56912124567", "cond_pago": "Crédito"},
    {"id": 26, "razon": "Asesorías Contables Norte", "rut": "98.765.432-1",
     "region": "Tarapacá", "comuna": "Iquique", "contacto": "Hugo Vásquez",
     "fono": "+56978780000", "cond_pago": "30 días"},
    {"id": 27, "razon": "Pesquera del Pacífico", "rut": "76.888.999-0",
     "region": "Biobío", "comuna": "Talcahuano", "contacto": "Loreto Silva",
     "fono": "+56990909090", "cond_pago": "15 días"},
    {"id": 28, "razon": "Viña El Encanto", "rut": "13.222.333-4",
     "region": "O'Higgins", "comuna": "Santa Cruz", "contacto": "Marcelo Correa",
     "fono": "+56932320000", "cond_pago": "Contado"},
    {"id": 29, "razon": "Maderas Cordillera", "rut": "14.555.666-7",
     "region": "Araucanía", "comuna": "Villarrica", "contacto": "Ricardo Pino",
     "fono": "+56912123456", "cond_pago": "30 días"},
    {"id": 30, "razon": "Transporte Expreso Sur", "rut": "19.999.888-7",
     "region": "Ñuble", "comuna": "San Carlos", "contacto": "Valentina Álvarez",
     "fono": "+56934340000", "cond_pago": "Crédito"},
]

def _next_id() -> int:
    return (max((c.get("id", 0) for c in CLIENTES), default=0) + 1)

# --------- Utils ---------
def login_required(fn):
    @wraps(fn)
    def _wrap(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login", next=request.path))
        return fn(*args, **kwargs)
    return _wrap

def responder(m: str) -> str:
    m = (m or "").lower()
    if "hola" in m: return "¡Hola! ¿En qué puedo ayudarte?"
    if "cómo estás" in m: return "¡Estoy bien, gracias! ¿Y tú?"
    if "adiós" in m or "bye" in m: return "¡Hasta luego!"
    if "instagram" in m or "ig" in m: return "¡Sí, este es un chat tipo IG! ¿Qué deseas saber?"
    return "No entendí tu mensaje. ¿Puedes repetirlo?"

def _norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.lower().strip()

# ---------- AUTH ----------
@app.get("/login")
def login():
    return render_template("login.html", error=None)

@app.post("/login")
def login_post():
    user = (request.form.get("user") or "").strip().lower()
    pwd = request.form.get("pwd") or ""
    if user in USERS and check_password_hash(USERS[user], pwd):
        session["user"] = user
        return redirect(request.args.get("next") or url_for("dashboard"))
    return render_template("login.html", error="Credenciales inválidas")

@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------- APP ----------
@app.get("/")
@login_required
def root():
    return redirect(url_for("dashboard"))


@app.get("/clientes")
@login_required
def clientes():
    q = (request.args.get("q") or "").strip()
    qn = _norm(q)
    data = CLIENTES
    if qn:
        keys = ("razon", "rut", "region", "comuna", "contacto", "fono")
        data = [c for c in CLIENTES if any(qn in _norm(c.get(k, "")) for k in keys)]
    return render_template("clientes.html", user=session.get("user"), clientes=data, q=q)

# ---------- API CLIENTES (CRUD) ----------
@app.post("/api/clientes")
@login_required
def crear_cliente():
    d = request.get_json(force=True) or {}
    if not (d.get("razon") and d.get("rut")):
        return jsonify({"ok": False, "error": "Razón Social y RUT son obligatorios."}), 400

    contacto_nombre = (d.get("contacto_nombre") or d.get("contacto") or "").strip()

    nuevo = {
        "id": _next_id(),
        "razon": (d.get("razon") or "").strip(),
        "rut": (d.get("rut") or "").strip(),
        "giro": (d.get("giro") or "").strip(),
        "region": (d.get("region") or "").strip(),
        "comuna": (d.get("comuna") or "").strip(),
        "fono": (d.get("fono") or "").strip(),
        "direccion": (d.get("direccion") or "").strip(),
        "notas": (d.get("notas") or "").strip(),
        # contacto
        "contacto": contacto_nombre or (d.get("contacto") or "").strip(),  # alias para la tabla
        "contacto_nombre": contacto_nombre,
        "contacto_email": (d.get("contacto_email") or "").strip(),
        "contacto_fono": (d.get("contacto_fono") or "").strip(),
        "contacto_cargo": (d.get("contacto_cargo") or "").strip(),
        "contacto_notas": (d.get("contacto_notas") or "").strip(),
    }
    CLIENTES.append(nuevo)
    return jsonify({"ok": True, "cliente": nuevo})

@app.put("/api/clientes/<int:cid>")
@login_required
def actualizar_cliente(cid: int):
    d = request.get_json(force=True) or {}
    for c in CLIENTES:
        if c.get("id") == cid:
            for k in (
                "razon","rut","giro","region","comuna","fono","direccion","notas",
                "contacto_nombre","contacto_email","contacto_fono","contacto_cargo","contacto_notas"
            ):
                if k in d:
                    c[k] = (d.get(k) or "").strip()
            # mantener alias 'contacto' para la tabla
            if "contacto_nombre" in d:
                cn = (d.get("contacto_nombre") or "").strip()
                if cn:
                    c["contacto"] = cn
            return jsonify({"ok": True, "cliente": c})
    return jsonify({"ok": False, "error": "Cliente no encontrado"}), 404

@app.delete("/api/clientes/<int:cid>")
@login_required
def eliminar_cliente(cid: int):
    global CLIENTES
    n0 = len(CLIENTES)
    CLIENTES = [c for c in CLIENTES if c.get("id") != cid]
    if len(CLIENTES) == n0:
        return jsonify({"ok": False, "error": "Cliente no encontrado"}), 404
    return jsonify({"ok": True})

# ---------- EXPORT ----------
@app.get("/clientes/export", endpoint="export_clientes")
@login_required
def export_clientes():
    import csv, io, datetime
    q = (request.args.get("q") or "").strip()
    qn = _norm(q)
    data = CLIENTES
    if qn:
        keys = ("razon","rut","region","comuna","contacto","fono")
        data = [c for c in CLIENTES if any(qn in _norm(c.get(k,"")) for k in keys)]

    buf = io.StringIO()
    buf.write("\ufeff")  # BOM para Excel
    w = csv.writer(buf)
    w.writerow(["Razón Social","RUT","Región","Comuna","Contacto","Teléfono"])
    for c in data:
        w.writerow([c.get("razon",""), c.get("rut",""), c.get("region",""),
                    c.get("comuna",""), c.get("contacto",""), c.get("fono","")])
    fname = f"clientes_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        buf.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={fname}"}
    )

# ---------- CHAT opcional ----------
@app.get("/chat")
@login_required
def chat_view():
    return render_template("index.html", user=session.get("user"))

@app.post("/api/chat")
@login_required
def api_chat():
    data = request.get_json(force=True) or {}
    return jsonify({"respuesta": responder(data.get("mensaje", ""))})



# ======= Ferrytruck / Ubicaciones =======
import datetime as dt

LAYOUT_UBI = [("A", 40), ("B", 40), ("C", 40), ("D", 40)]
UBICACIONES = []  # [{id,codigo,fila,nro,estado,vin,patente,marca,color,notas,updated_at}]

def _init_ubicaciones():
    if UBICACIONES:
        return
    _id = 1
    for fila, count in LAYOUT_UBI:
        for i in range(1, count+1):
            UBICACIONES.append({
                "id": _id,
                "codigo": f"{fila}-{i:03d}",
                "fila": fila, "nro": i,
                "estado": "libre",
                "vin": "", "patente": "", "marca": "", "color": "", "notas": "",
                "updated_at": dt.datetime.utcnow().isoformat()
            })
            _id += 1

def _find_ubi(uid:int):
    for u in UBICACIONES:
        if u["id"] == uid:
            return u
    return None

@app.get("/ferrytruck")
@login_required
def ferrytruck_root():
    return redirect(url_for("ferrytruck_ubicaciones"))

@app.get("/ferrytruck/ubicaciones")
@login_required
def ferrytruck_ubicaciones():
    _init_ubicaciones()
    data = sorted(UBICACIONES, key=lambda x: (x["fila"], x["nro"]))
    return render_template("ferrytruck_ubicaciones.html", ubicaciones=data)

@app.get("/api/ferrytruck/ubicaciones")
@login_required
def api_ft_list():
    _init_ubicaciones()
    return jsonify(ok=True, ubicaciones=UBICACIONES)

@app.put("/api/ferrytruck/ubicaciones/<int:uid>")
@login_required
def api_ft_update(uid:int):
    _init_ubicaciones()
    u = _find_ubi(uid)
    if not u:
        return jsonify(ok=False, error="Ubicación no encontrada"), 404
    d = request.get_json(force=True) or {}
    for k in ("estado","vin","patente","marca","color","notas"):
        if k in d: u[k] = (d.get(k) or "").strip()
    if u["estado"] not in ("libre","ocupado","reservado","salida"):
        u["estado"] = "libre"
    u["updated_at"] = dt.datetime.utcnow().isoformat()
    return jsonify(ok=True, ubicacion=u)

@app.post("/api/ferrytruck/ubicaciones/reset")
@login_required
def api_ft_reset():
    _init_ubicaciones()
    for u in UBICACIONES:
        u.update({"estado":"libre","vin":"","patente":"","marca":"","color":"","notas":""})
        u["updated_at"] = dt.datetime.utcnow().isoformat()
    return jsonify(ok=True)

@app.get("/ferrytruck/ubicaciones/export", endpoint="ferrytruck_export")
@login_required
def ferrytruck_export():
    import csv, io, datetime
    _init_ubicaciones()
    buf = io.StringIO(); buf.write("\ufeff")
    w = csv.writer(buf)
    w.writerow(["Código","Fila","N°","Estado","VIN","Patente","Marca","Color","Notas","Actualizado"])
    for u in sorted(UBICACIONES, key=lambda x:(x["fila"], x["nro"])):
        w.writerow([u["codigo"], u["fila"], u["nro"], u["estado"], u["vin"], u["patente"], u["marca"], u["color"], u["notas"], u["updated_at"]])
    fname = f"ubicaciones_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(buf.getvalue(), mimetype="text/csv; charset=utf-8",
                    headers={"Content-Disposition": f"attachment; filename={fname}"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

# --------- INVENTARIO (demo en memoria) ---------
ARTICULOS = [
    {
        "id": 1,
        "cod_int": "AV-0001",
        "cod_ext": "PROV-8891",
        "categoria": "Parabrisas",
        "subcategoria": "Delantero",
        "marca": "Toyota",
        "modelo": "Yaris",
        "anio": "2018-2022",
        "descripcion": "Parabrisas laminado templado con sensor de lluvia",
        "precio_venta": 129990,
        "stock_total": 24,
        "estado": "Activo",
        "compatibilidad": "XP150",
        "atributos": {"material":"Laminado","color":"Transparente","dimensiones":"1410x820x6mm","peso":"12kg","volumen":"0.12m³"},
        "inventario": {"costo": 82900, "proveedor": "Cristales Andes", "bodegas": {"Central": 14, "Sucursal Norte": 10}},
        "imagenes": ["/static/sprites/parabrisas_ejemplo.jpeg"],
        "fabricante": "Fuyao",
        "cod_proveedor": "FY-TOY-YAR-18D",
        "unidad": "un",
        "moneda": "CLP",
        "etiquetas": ["sensor", "laminado"],
        "estado_comercial": "Normal",
        "observaciones": ""
    },
    {
        "id": 2,
        "cod_int": "AV-0002",
        "cod_ext": "PROV-7742",
        "categoria": "Lunas",
        "subcategoria": "Trasera",
        "marca": "Hyundai",
        "modelo": "Accent",
        "anio": "2017-2023",
        "descripcion": "Luna trasera templada con desempañador",
        "precio_venta": 89990,
        "stock_total": 7,
        "estado": "Activo",
        "compatibilidad": "HC/HCi",
        "atributos": {"material":"Templado","color":"Verde","dimensiones":"1310x720x5mm","peso":"9kg","volumen":"0.09m³"},
        "inventario": {"costo": 55900, "proveedor": "Vidrios Pacífico", "bodegas": {"Central": 5, "Sucursal Sur": 2}},
        "imagenes": ["/static/demo/av0002_1.jpg"],
        "fabricante": "AGC",
        "cod_proveedor": "AGC-HYU-ACE-17T",
        "unidad": "un",
        "moneda": "CLP",
        "etiquetas": ["desempañador"],
        "estado_comercial": "Normal",
        "observaciones": ""
    },
]

def _art_sets():
    cat = sorted({a.get("categoria","") for a in ARTICULOS if a.get("categoria")})
    sub = sorted({a.get("subcategoria","") for a in ARTICULOS if a.get("subcategoria")})
    marca = sorted({a.get("marca","") for a in ARTICULOS if a.get("marca")})
    modelo = sorted({a.get("modelo","") for a in ARTICULOS if a.get("modelo")})
    anio = sorted({a.get("anio","") for a in ARTICULOS if a.get("anio")})
    estado = ["Activo","Inactivo"]
    return cat, sub, marca, modelo, anio, estado

def _norm_s(s:str)->str:
    import unicodedata
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.lower().strip()

def _filtrar_articulos(args):
    q = _norm_s(args.get("q",""))
    fcat, fsub = args.get("categoria",""), args.get("subcategoria","")
    fmarca, fmodelo = args.get("marca",""), args.get("modelo","")
    fanio, festado = args.get("anio",""), args.get("estado","")
    datos = ARTICULOS
    def ok(a):
        if q:
            blob = " ".join([
                a.get("cod_int",""),
                a.get("descripcion",""), a.get("compatibilidad",""),
                a.get("marca",""), a.get("modelo",""), a.get("anio","")
            ])
            if q not in _norm_s(blob): return False
        if fcat and a.get("categoria") != fcat: return False
        if fsub and a.get("subcategoria") != fsub: return False
        if fmarca and a.get("marca") != fmarca: return False
        if fmodelo and a.get("modelo") != fmodelo: return False
        if fanio and a.get("anio") != fanio: return False
        if festado and a.get("estado") != festado: return False
        return True
    return [a for a in datos if ok(a)]

@app.get("/inventario")
@login_required
def inventario_listado():
    cat, sub, marca, modelo, anio, estado = _art_sets()

    # 🔑 recolectar todas las bodegas únicas
    bodegas = set()
    for a in ARTICULOS:
        inv = a.get("inventario", {})
        if "bodegas" in inv:
            bodegas.update(inv["bodegas"].keys())

    return render_template(
        "inventario.html",
        user=session.get("user"),
        articulos=ARTICULOS,
        cat=cat,
        sub=sub,
        marca=marca,
        modelo=modelo,
        anio=anio,
        estados=estado,       # si aún usas "estado"
        bodegas=sorted(bodegas)  # 👈 aquí va la lista de bodegas
    )


@app.get("/api/articulos/<int:aid>")
@login_required
def api_articulo(aid:int):
    a = next((x for x in ARTICULOS if x.get("id")==aid), None)
    if not a: return jsonify({"ok": False, "error":"No encontrado"}), 404
    return jsonify({"ok": True, "articulo": a})

@app.get("/inventario/export")
@login_required
def inventario_export():
    import csv, io, datetime
    data = _filtrar_articulos(request.args)
    buf = io.StringIO(); buf.write("\ufeff")
    w = csv.writer(buf)
    # columnas alineadas a la tabla visible
    w.writerow(["Código interno","Categoría","Marca/Modelo/Año","Descripción","Precio venta","Stock total"])
    for a in data:
        mma = f'{a.get("marca","")} {a.get("modelo","")} {a.get("anio","")}'.strip()
        w.writerow([
            a.get("cod_int",""), a.get("categoria",""), mma,
            a.get("descripcion",""), a.get("precio_venta",""), a.get("stock_total","")
        ])
    fname = f"articulos_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(buf.getvalue(), mimetype="text/csv; charset=utf-8",
                    headers={"Content-Disposition": f"attachment; filename={fname}"})


@app.route("/cotizador")
@login_required
def cotizador():
    # pasa artículos y clientes al template para buscador y datalist
    return render_template(
        "cotizador.html",
        title="Cotizador",
        articulos=ARTICULOS,
        clientes=CLIENTES
    )



# Cotizaciones de ejemplo
COTIZACIONES = [
    {
        "id": 1,
        "cliente": "Juan Pérez",
        "fecha": "2025-09-14",
        "estado": "Pendiente",
        "items": [
            {"descripcion": "Parabrisas Toyota Yaris 2018–2022", "cantidad": 2, "precio": 129990},
            {"descripcion": "Instalación", "cantidad": 1, "precio": 50000},
        ],
        "total": 309980,
    }
]


from flask import render_template, jsonify, Response

@app.get("/cotizaciones")
@login_required
def cotizaciones():
    return render_template("cotizaciones.html", cotizaciones=COTIZACIONES)

@app.delete("/api/cotizaciones/<int:cid>")
@login_required
def cotizacion_delete(cid):
    global COTIZACIONES
    COTIZACIONES = [c for c in COTIZACIONES if c["id"] != cid]
    return jsonify(ok=True)

@app.get("/cotizaciones/export")
@login_required
def cotizaciones_export():
    import csv, io, datetime
    buf = io.StringIO()
    buf.write("\ufeff")  # BOM para Excel

    writer = csv.writer(buf)
    # Cabecera del archivo
    writer.writerow([
        "N° Cotización",
        "Cliente",
        "Fecha",
        "Estado",
        "Producto",
        "Cantidad",
        "Precio Unitario",
        "Subtotal"
    ])

    # Recorremos cotizaciones
    for c in COTIZACIONES:
        # seguridad: si no tiene items, saltamos
        items = c.get("items", [])
        if not items:
            writer.writerow([
                c["id"],
                c["cliente"],
                c["fecha"],
                c["estado"],
                "(Sin productos)",
                "",
                "",
                ""
            ])
        else:
            for it in items:
                cantidad = it.get("qty", 1)
                precio = it.get("price", 0)
                subtotal = cantidad * precio

                writer.writerow([
                    c["id"],
                    c["cliente"],
                    c["fecha"],
                    c["estado"],
                    it.get("nombre") or it.get("descripcion", ""),
                    cantidad,
                    precio,
                    subtotal
                ])

    # Respuesta
    return Response(
        buf.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=cotizaciones_{datetime.date.today()}.csv"
        }
    )

    
@app.get("/api/cotizaciones/<int:cid>")
@login_required
def cotizacion_get(cid):
    c = next((x for x in COTIZACIONES if x["id"] == cid), None)
    if not c:
        return jsonify(ok=False, error="No encontrado"), 404

    # ⚡ Ejemplo: agrega items simulados
    items = [
        {"descripcion": "Parabrisas Toyota Yaris 2018–2022", "precio": 129990}
    ]

    return jsonify(ok=True, cotizacion=c, items=items)



# ======== SOPORTE / TICKETS ========
import os, datetime as dt
from flask import send_from_directory

TICKETS = []  # [{id, creado_at, estado, asunto, categoria, prioridad, modulo, cliente, contacto, email, fono, url, descripcion, pasos, impacto, archivos:[{name,path,size}], tags:list}]
UPLOAD_DIR = os.path.join(app.static_folder, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def _next_tid() -> int:
    return (max((t.get("id", 0) for t in TICKETS), default=0) + 1)

@app.get("/soporte")
@login_required
def soporte_view():
    # módulos para el select, reusa tus vistas conocidas
    modulos = ["Dashboard","Clientes","Inventario","Cotizador","Cotizaciones","Ventas","Ferrytruck","Login","Otro"]
    return render_template("soporte.html", user=session.get("user"), tickets=TICKETS, modulos=modulos)

@app.post("/api/soporte")
@login_required
def soporte_create():
    # Maneja multipart/form-data con adjuntos
    f = request.form
    files = request.files.getlist("adjuntos")
    saved = []
    for file in files:
        if not file or not file.filename:
            continue
        # nombre seguro simple
        fname = f"{dt.datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename.replace(' ','_')}"
        dest = os.path.join(UPLOAD_DIR, fname)
        file.save(dest)
        saved.append({"name": file.filename, "path": f"/static/uploads/{fname}", "size": os.path.getsize(dest)})

    t = {
        "id": _next_tid(),
        "creado_at": dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
        "estado": "Nuevo",
        "asunto": (f.get("asunto") or "").strip(),
        "categoria": (f.get("categoria") or "Consulta").strip(),
        "prioridad": (f.get("prioridad") or "Media").strip(),
        "modulo": (f.get("modulo") or "Otro").strip(),
        "cliente": (f.get("cliente") or "").strip(),
        "contacto": (f.get("contacto") or "").strip(),
        "email": (f.get("email") or "").strip(),
        "fono": (f.get("fono") or "").strip(),
        "url": (f.get("url") or "").strip(),
        "descripcion": (f.get("descripcion") or "").strip(),
        "pasos": (f.get("pasos") or "").strip(),
        "impacto": (f.get("impacto") or "").strip(),
        "tags": [x.strip() for x in (f.get("tags") or "").split(",") if x.strip()],
        "archivos": saved,
    }
    if not t["asunto"] or not t["descripcion"]:
        return jsonify(ok=False, error="Asunto y descripción son obligatorios"), 400

    TICKETS.append(t)
    return jsonify(ok=True, ticket=t)

@app.delete("/api/soporte/<int:tid>")
@login_required
def soporte_delete(tid:int):
    global TICKETS
    pre = len(TICKETS)
    TICKETS = [x for x in TICKETS if x.get("id") != tid]
    if len(TICKETS) == pre:
        return jsonify(ok=False, error="Ticket no encontrado"), 404
    return jsonify(ok=True)

@app.get("/soporte/export")
@login_required
def soporte_export():
    import csv, io
    buf = io.StringIO(); buf.write("\ufeff")
    w = csv.writer(buf)
    w.writerow(["ID","Fecha","Estado","Asunto","Categoría","Prioridad","Módulo","Cliente","Contacto","Email","Fono","URL","Impacto","Tags"])
    for t in TICKETS:
        w.writerow([
            t["id"], t["creado_at"], t["estado"], t["asunto"], t["categoria"], t["prioridad"], t["modulo"],
            t["cliente"], t["contacto"], t["email"], t["fono"], t["url"], t["impacto"], ";".join(t["tags"])
        ])
    fname = f"tickets_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(buf.getvalue(), mimetype="text/csv; charset=utf-8",
                    headers={"Content-Disposition": f"attachment; filename={fname}"})


# ============================
# RUTA: Listado de Pedidos
# ============================
@app.route("/pedidos")
@login_required
def pedidos():
    # Aquí podrías traer los pedidos desde la base de datos.
    # De momento uso datos de ejemplo (mock).
    pedidos = [
        {
            "id": 1,
            "numero": 1,
            "cotizacion_id": 101,
            "cliente": "Juan Pérez",
            "fecha": "2025-09-14",
            "fecha_entrega": "2025-09-20",
            "cond_pago": "30 días",
            "estado_entrega": "Pendiente",
            "estado_prod": "En producción",
            "total": 154690
        },
        {
            "id": 2,
            "numero": 2,
            "cotizacion_id": 102,
            "cliente": "Empresa X",
            "fecha": "2025-09-13",
            "fecha_entrega": "2025-09-25",
            "cond_pago": "Contado",
            "estado_entrega": "Entregado",
            "estado_prod": "Finalizado",
            "total": 320000
        }
    ]
    return render_template("pedidos.html", title="Pedidos", pedidos=pedidos)

# ================== DASHBOARD ==================
@app.route("/dashboard")
@login_required
def dashboard():
    # KPIs dummy
    kpis = {
        "ventas_mes": 154690,
        "ventas_variacion": "+12%",
        "cotizaciones": 32,
        "conversion": "65%",
        "pedidos": 18,
        "pedidos_produccion": 5,
        "clientes_nuevos": 7
    }

    # Datos dummy para los gráficos
    chart_data = {
        "estados": {
            "labels": ["Pendiente", "En producción", "Finalizado"],
            "values": [5, 8, 12]
        },
        "ventas": {
            "labels": ["Ene","Feb","Mar","Abr","May","Jun"],
            "values": [120000,150000,180000,140000,200000,154690]
        },
        "coti_pedidos": {
            "labels": ["Ene","Feb","Mar","Abr","May","Jun"],
            "cotizaciones": [20,25,22,30,28,32],
            "pedidos": [10,18,15,20,25,18]
        }
    }

    return render_template(
        "dashboard.html",
        title="Dashboard",
        kpis=kpis,
        chart_data=chart_data
    )

@app.route("/configuracion/empresa")
@login_required
def config_empresa():
    # Mock de datos actuales de la empresa
    empresa = {
        "nombre": "AutoVidrios Ltda.",
        "rut": "76.123.456-7",
        "direccion": "Av. Las Industrias 1234, Santiago",
        "telefono": "+56 2 2345 6789",
        "logo": "/static/demo/logo.png",
        "prefijo_cot": "COT-",
        "prefijo_ped": "PED-",
        "correlativo_cot": 101,
        "correlativo_ped": 55,
        "iva": 19,
        "descuento_general": 5,
    }
    return render_template("config_empresa.html", title="Datos de la Empresa", empresa=empresa)



#-------------------------------------------------------------------------


# ======== ROLES & PERMISSIONS (demo en memoria) ========
# Catálogo de permisos (module + action => code)
PERMISSION_CATALOG = [
    # Dashboard
    {"code":"dashboard.view", "module":"Dashboard", "action":"view"},
    {"code":"dashboard.admin","module":"Dashboard", "action":"admin"},
    # Clientes
    {"code":"clientes.view","module":"Clientes","action":"view"},
    {"code":"clientes.create","module":"Clientes","action":"create"},
    {"code":"clientes.edit","module":"Clientes","action":"edit"},
    {"code":"clientes.delete","module":"Clientes","action":"delete"},
    {"code":"clientes.export","module":"Clientes","action":"export"},
    # Inventario
    {"code":"inventario.view","module":"Inventario","action":"view"},
    {"code":"inventario.create","module":"Inventario","action":"create"},
    {"code":"inventario.edit","module":"Inventario","action":"edit"},
    {"code":"inventario.delete","module":"Inventario","action":"delete"},
    {"code":"inventario.export","module":"Inventario","action":"export"},
    # Ventas / Cotizaciones / Pedidos
    {"code":"cotizaciones.view","module":"Cotizaciones","action":"view"},
    {"code":"cotizaciones.create","module":"Cotizaciones","action":"create"},
    {"code":"cotizaciones.edit","module":"Cotizaciones","action":"edit"},
    {"code":"cotizaciones.delete","module":"Cotizaciones","action":"delete"},
    {"code":"cotizaciones.export","module":"Cotizaciones","action":"export"},

    {"code":"pedidos.view","module":"Pedidos","action":"view"},
    {"code":"pedidos.create","module":"Pedidos","action":"create"},
    {"code":"pedidos.edit","module":"Pedidos","action":"edit"},
    {"code":"pedidos.delete","module":"Pedidos","action":"delete"},
    {"code":"pedidos.export","module":"Pedidos","action":"export"},

    # Configuración
    {"code":"config.view","module":"Configuración","action":"view"},
    {"code":"config.edit","module":"Configuración","action":"edit"},
    {"code":"config.admin","module":"Configuración","action":"admin"},

    # Soporte
    {"code":"soporte.view","module":"Soporte","action":"view"},
    {"code":"soporte.create","module":"Soporte","action":"create"},
    {"code":"soporte.edit","module":"Soporte","action":"edit"},
    {"code":"soporte.delete","module":"Soporte","action":"delete"},
    {"code":"soporte.export","module":"Soporte","action":"export"},
]

def _perm_codes_all():
    return [p["code"] for p in PERMISSION_CATALOG]

# Usuarios disponibles para asignar (de tu USERS demo)
def _user_list():
    return [{"username": u} for u in USERS.keys()]

# Datos en memoria
ROLES = [
    {
        "id": 1,
        "name": "Administrador",
        "desc": "Acceso total (rol del sistema)",
        "permissions": _perm_codes_all(),
        "users": ["admin"],         # admin por defecto
        "is_system": True
    },
    {
        "id": 2,
        "name": "Vendedor",
        "desc": "Gestiona cotizaciones y pedidos",
        "permissions": [
            "dashboard.view",
            "clientes.view",
            "cotizaciones.view","cotizaciones.create","cotizaciones.edit","cotizaciones.export",
            "pedidos.view","pedidos.create","pedidos.edit","pedidos.export",
        ],
        "users": ["francisco"],
        "is_system": False
    },
    {
        "id": 3,
        "name": "Bodega",
        "desc": "Consulta de inventario y exportación",
        "permissions": ["inventario.view","inventario.export","dashboard.view"],
        "users": [],
        "is_system": False
    },
]

def _role_next_id() -> int:
    return (max((r.get("id",0) for r in ROLES), default=0) + 1)

# ===== VISTA: Página de Roles
@app.get("/roles")
@login_required
def roles_view():
    return render_template(
        "roles.html",
        roles=ROLES,
        users=_user_list(),
        perm_catalog=PERMISSION_CATALOG
    )

# ===== API: Listado de roles
@app.get("/api/roles")
@login_required
def roles_list():
    return jsonify(ok=True, roles=ROLES)

# ===== API: Crear rol
@app.post("/api/roles")
@login_required
def roles_create():
    data = request.get_json(force=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify(ok=False, error="Nombre es obligatorio"), 400
    if any(r["name"].lower()==name.lower() for r in ROLES):
        return jsonify(ok=False, error="Ya existe un rol con ese nombre"), 400

    r = {
        "id": _role_next_id(),
        "name": name,
        "desc": (data.get("desc") or "").strip(),
        "permissions": [c for c in (data.get("permissions") or []) if c in _perm_codes_all()],
        "users": list(set(data.get("users") or [])),
        "is_system": False
    }
    ROLES.append(r)
    return jsonify(ok=True, role=r)

# ===== API: Actualizar nombre/desc
@app.put("/api/roles/<int:rid>")
@login_required
def roles_update(rid:int):
    data = request.get_json(force=True) or {}
    role = next((x for x in ROLES if x["id"]==rid), None)
    if not role:
        return jsonify(ok=False, error="Rol no encontrado"), 404
    if role.get("is_system"):
        # puedes permitir cambiar desc, pero no el nombre
        role["desc"] = (data.get("desc") or role.get("desc","")).strip()
        return jsonify(ok=True, role=role)

    name = (data.get("name") or role["name"]).strip()
    if not name:
        return jsonify(ok=False, error="Nombre es obligatorio"), 400
    if any(x["id"]!=rid and x["name"].lower()==name.lower() for x in ROLES):
        return jsonify(ok=False, error="Ya existe otro rol con ese nombre"), 400

    role["name"] = name
    role["desc"] = (data.get("desc") or role.get("desc","")).strip()
    return jsonify(ok=True, role=role)

# ===== API: Eliminar rol
@app.delete("/api/roles/<int:rid>")
@login_required
def roles_delete(rid:int):
    global ROLES
    role = next((x for x in ROLES if x["id"]==rid), None)
    if not role:
        return jsonify(ok=False, error="Rol no encontrado"), 404
    if role.get("is_system"):
        return jsonify(ok=False, error="Este rol es del sistema y no puede eliminarse"), 400
    ROLES = [x for x in ROLES if x["id"]!=rid]
    return jsonify(ok=True)

# ===== API: Actualizar permisos de un rol
@app.put("/api/roles/<int:rid>/permissions")
@login_required
def roles_update_perms(rid:int):
    data = request.get_json(force=True) or {}
    role = next((x for x in ROLES if x["id"]==rid), None)
    if not role:
        return jsonify(ok=False, error="Rol no encontrado"), 404
    allowed = set(_perm_codes_all())
    role["permissions"] = [c for c in (data.get("permissions") or []) if c in allowed]
    return jsonify(ok=True, role=role)

# ===== API: Asignar usuarios a un rol
@app.put("/api/roles/<int:rid>/users")
@login_required
def roles_update_users(rid:int):
    data = request.get_json(force=True) or {}
    role = next((x for x in ROLES if x["id"]==rid), None)
    if not role:
        return jsonify(ok=False, error="Rol no encontrado"), 404
    users = [u["username"] for u in _user_list()]
    role["users"] = [u for u in (data.get("users") or []) if u in users]
    return jsonify(ok=True, role=role)

# ===== Export CSV de roles
@app.get("/roles/export")
@login_required
def roles_export():
    import csv, io, datetime as dt
    buf = io.StringIO(); buf.write("\ufeff")
    w = csv.writer(buf)
    w.writerow(["ID","Rol","Descripción","#Permisos","#Usuarios","Sistema"])
    for r in ROLES:
        w.writerow([r["id"], r["name"], r.get("desc",""), len(r.get("permissions",[])), len(r.get("users",[])), "Sí" if r.get("is_system") else "No"])
    fname = f"roles_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(buf.getvalue(), mimetype="text/csv; charset=utf-8",
                    headers={"Content-Disposition": f"attachment; filename={fname}"})


# ===== USUARIOS (in-memory demo) =====
USERS_DB = [
    {"id":1,"username":"admin","email":"admin@local","role":"Administrador","active":True,"last_login":"2025-01-01","is_system":True},
    {"id":2,"username":"francisco","email":"fran@local","role":"Cliente","active":True,"last_login":"2025-01-10","is_system":False},
]

def _user_next_id():
    return max([u["id"] for u in USERS_DB], default=0)+1

@app.get("/usuarios")
@login_required
def usuarios_view():
    return render_template("usuarios.html", users=USERS_DB, roles=ROLES)

@app.get("/api/usuarios/<int:uid>")
@login_required
def usuarios_get(uid:int):
    u = next((x for x in USERS_DB if x["id"]==uid),None)
    if not u: return jsonify(ok=False,error="Usuario no encontrado"),404
    return jsonify(ok=True,user=u)

@app.post("/api/usuarios")
@login_required
def usuarios_create():
    d = request.get_json(force=True) or {}
    if not d.get("username") or not d.get("email"):
        return jsonify(ok=False,error="Faltan datos"),400
    if any(u["username"]==d["username"] for u in USERS_DB):
        return jsonify(ok=False,error="Usuario ya existe"),400
    u = {
        "id":_user_next_id(),
        "username":d["username"],
        "email":d["email"],
        "role":d.get("role") or "Cliente",
        "active":bool(d.get("active",True)),
        "last_login":None,
        "is_system":False
    }
    USERS_DB.append(u)
    return jsonify(ok=True,user=u)

@app.put("/api/usuarios/<int:uid>")
@login_required
def usuarios_update(uid:int):
    u = next((x for x in USERS_DB if x["id"]==uid),None)
    if not u: return jsonify(ok=False,error="Usuario no encontrado"),404
    if u.get("is_system"): return jsonify(ok=False,error="Usuario protegido"),400
    d = request.get_json(force=True) or {}
    u["email"] = d.get("email",u["email"])
    u["role"] = d.get("role",u["role"])
    u["active"]= bool(d.get("active",u["active"]))
    return jsonify(ok=True,user=u)

@app.delete("/api/usuarios/<int:uid>")
@login_required
def usuarios_delete(uid:int):
    global USERS_DB
    u = next((x for x in USERS_DB if x["id"]==uid),None)
    if not u: return jsonify(ok=False,error="Usuario no encontrado"),404
    if u.get("is_system"): return jsonify(ok=False,error="Usuario protegido"),400
    USERS_DB = [x for x in USERS_DB if x["id"]!=uid]
    return jsonify(ok=True)

@app.get("/usuarios/export")
@login_required
def usuarios_export():
    import csv,io,datetime as dt
    buf=io.StringIO(); buf.write("\ufeff")
    w=csv.writer(buf)
    w.writerow(["ID","Usuario","Email","Rol","Activo","Último acceso"])
    for u in USERS_DB:
        w.writerow([u["id"],u["username"],u["email"],u["role"],"Sí" if u["active"] else "No",u["last_login"] or "-"])
    fname=f"usuarios_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(buf.getvalue(),mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition":f"attachment; filename={fname}"})

#-------------------------------------------------------------------------


# ================== CONFIGURACIÓN DE VENTAS ==================
from flask import request, jsonify, render_template
from copy import deepcopy

# --- Datos base (memoria) ---
PAGOS = [
    {"id": 1, "nombre": "Contado",   "dias": 0,  "default": True,  "activo": True,  "orden": 1},
    {"id": 2, "nombre": "30 días",   "dias": 30, "default": False, "activo": True,  "orden": 2},
    {"id": 3, "nombre": "Crédito",   "dias": 45, "default": False, "activo": True,  "orden": 3},
]

ENTREGAS = [
    {"id": 1, "nombre": "Retiro en bodega", "tipo": "retiro",   "dias": 0,  "costo": 0,    "default": True,  "activo": True, "orden": 1},
    {"id": 2, "nombre": "Despacho",         "tipo": "despacho", "dias": 2,  "costo": 5000, "default": False, "activo": True, "orden": 2},
]

ESTADOS = {
    "pedidos": [
        {"id": 1, "nombre": "Pendiente",     "color": "#fde68a", "default": True,  "finaliza": False, "activo": True, "orden": 1},
        {"id": 2, "nombre": "En preparación","color": "#a7f3d0", "default": False, "finaliza": False, "activo": True, "orden": 2},
        {"id": 3, "nombre": "Entregado",     "color": "#bbf7d0", "default": False, "finaliza": True,  "activo": True, "orden": 3},
    ],
    "produccion": [
        {"id": 1, "nombre": "En producción", "color": "#bae6fd", "default": True,  "finaliza": False, "activo": True, "orden": 1},
        {"id": 2, "nombre": "Finalizado",    "color": "#86efac", "default": False, "finaliza": True,  "activo": True, "orden": 2},
    ],
    "soporte": [
        {"id": 1, "nombre": "Nuevo",         "color": "#fca5a5", "default": True,  "finaliza": False, "activo": True, "orden": 1},
        {"id": 2, "nombre": "En curso",      "color": "#fde68a", "default": False, "finaliza": False, "activo": True, "orden": 2},
        {"id": 3, "nombre": "Resuelto",      "color": "#bbf7d0", "default": False, "finaliza": True,  "activo": True, "orden": 3},
    ],
}

BODEGAS = [
    {"id": 1, "codigo":"BOD-001","nombre":"Bodega Central","tipo":"bodega","direccion":"Av. Matta 1234","capacidad":500,"responsable":"Carlos Pérez","activo":True,"orden":1},
    {"id": 2, "codigo":"SUC-001","nombre":"Sucursal Norte","tipo":"sucursal","direccion":"Av. Los Andes 88","capacidad":200,"responsable":"María Soto","activo":True,"orden":2},
]

def _next_id(lst):
    return (max((x.get("id",0) for x in lst), default=0) + 1)

def _reorder(lst):
    for i, x in enumerate(sorted(lst, key=lambda z: z["orden"]), start=1):
        x["orden"] = i

def _move(lst, _id, direction):
    lst.sort(key=lambda z: z["orden"])
    idx = next((i for i,x in enumerate(lst) if x["id"]==_id), None)
    if idx is None: return False
    if direction == "up" and idx>0:
        lst[idx]["orden"], lst[idx-1]["orden"] = lst[idx-1]["orden"], lst[idx]["orden"]
    elif direction == "down" and idx < len(lst)-1:
        lst[idx]["orden"], lst[idx+1]["orden"] = lst[idx+1]["orden"], lst[idx]["orden"]
    _reorder(lst); return True

@app.get("/configuracion/ventas")
@login_required
def config_ventas():
    pagos = sorted(PAGOS, key=lambda x: x["orden"])
    entregas = sorted(ENTREGAS, key=lambda x: x["orden"])
    estados = {g: sorted(lst, key=lambda x: x["orden"]) for g,lst in ESTADOS.items()}
    bodegas = sorted(BODEGAS, key=lambda x: x["orden"])
    return render_template("config_ventas.html",
                           user=session.get("user"),
                           pagos=pagos, entregas=entregas, estados=estados, bodegas=bodegas)

# ---- Pago
@app.post("/api/conf/ventas/pago")
@login_required
def api_pago_create():
    d = request.get_json(force=True) or {}
    if not d.get("nombre"): return jsonify(ok=False, error="Nombre requerido"), 400
    item = {
        "id": _next_id(PAGOS),
        "nombre": d.get("nombre","").strip(),
        "dias": int(d.get("dias") or 0),
        "default": False,
        "activo": bool(int(d.get("activo", 1))),
        "orden": len(PAGOS)+1
    }
    PAGOS.append(item)
    return jsonify(ok=True, item=item)

@app.put("/api/conf/ventas/pago/<int:pid>")
@login_required
def api_pago_update(pid):
    d = request.get_json(force=True) or {}
    for x in PAGOS:
        if x["id"]==pid:
            x["nombre"] = d.get("nombre", x["nombre"]).strip()
            x["dias"]   = int(d.get("dias", x["dias"]))
            x["activo"] = bool(int(d.get("activo", int(x["activo"]))))
            return jsonify(ok=True, item=x)
    return jsonify(ok=False, error="No encontrado"), 404

@app.delete("/api/conf/ventas/pago/<int:pid>")
@login_required
def api_pago_delete(pid):
    global PAGOS
    pre = len(PAGOS)
    PAGOS = [x for x in PAGOS if x["id"]!=pid]
    _reorder(PAGOS)
    if len(PAGOS)==pre: return jsonify(ok=False, error="No encontrado"), 404
    return jsonify(ok=True)

@app.post("/api/conf/ventas/pago/<int:pid>/default")
@login_required
def api_pago_default(pid):
    found = False
    for x in PAGOS:
        if x["id"]==pid: x["default"]=True; found=True
        else: x["default"]=False
    if not found: return jsonify(ok=False, error="No encontrado"), 404
    return jsonify(ok=True)

@app.post("/api/conf/ventas/pago/<int:pid>/move")
@login_required
def api_pago_move(pid):
    d = request.get_json(force=True) or {}
    ok = _move(PAGOS, pid, d.get("direction"))
    return jsonify(ok=ok)

# ---- Entrega
@app.post("/api/conf/ventas/entrega")
@login_required
def api_entrega_create():
    d = request.get_json(force=True) or {}
    if not d.get("nombre"): return jsonify(ok=False, error="Nombre requerido"), 400
    item = {
        "id": _next_id(ENTREGAS),
        "nombre": d.get("nombre","").strip(),
        "tipo": (d.get("tipo") or "retiro").strip(),
        "dias": int(d.get("dias") or 0),
        "costo": int(d.get("costo") or 0),
        "default": False,
        "activo": bool(int(d.get("activo", 1))),
        "orden": len(ENTREGAS)+1
    }
    ENTREGAS.append(item)
    return jsonify(ok=True, item=item)

@app.put("/api/conf/ventas/entrega/<int:eid>")
@login_required
def api_entrega_update(eid):
    d = request.get_json(force=True) or {}
    for x in ENTREGAS:
        if x["id"]==eid:
            x["nombre"] = d.get("nombre", x["nombre"]).strip()
            x["tipo"]   = (d.get("tipo", x["tipo"]) or "retiro").strip()
            x["dias"]   = int(d.get("dias", x["dias"]))
            x["costo"]  = int(d.get("costo", x["costo"]))
            x["activo"] = bool(int(d.get("activo", int(x["activo"]))))
            return jsonify(ok=True, item=x)
    return jsonify(ok=False, error="No encontrado"), 404

@app.delete("/api/conf/ventas/entrega/<int:eid>")
@login_required
def api_entrega_delete(eid):
    global ENTREGAS
    pre=len(ENTREGAS)
    ENTREGAS=[x for x in ENTREGAS if x["id"]!=eid]
    _reorder(ENTREGAS)
    if len(ENTREGAS)==pre: return jsonify(ok=False, error="No encontrado"), 404
    return jsonify(ok=True)

@app.post("/api/conf/ventas/entrega/<int:eid>/default")
@login_required
def api_entrega_default(eid):
    found=False
    for x in ENTREGAS:
        if x["id"]==eid: x["default"]=True; found=True
        else: x["default"]=False
    if not found: return jsonify(ok=False, error="No encontrado"), 404
    return jsonify(ok=True)

@app.post("/api/conf/ventas/entrega/<int:eid>/move")
@login_required
def api_entrega_move(eid):
    d=request.get_json(force=True) or {}
    ok=_move(ENTREGAS, eid, d.get("direction"))
    return jsonify(ok=ok)

# ---- Estados
@app.post("/api/conf/ventas/estado/<grupo>")
@login_required
def api_estado_create(grupo):
    if grupo not in ESTADOS: return jsonify(ok=False, error="Grupo inválido"), 400
    d=request.get_json(force=True) or {}
    if not d.get("nombre") or not d.get("color"):
        return jsonify(ok=False, error="Nombre y color requeridos"), 400
    lst = ESTADOS[grupo]
    item = {
        "id": _next_id(lst),
        "nombre": d.get("nombre","").strip(),
        "color": d.get("color","#22d3ee").strip(),
        "default": False,
        "finaliza": bool(int(d.get("finaliza", 0))),
        "activo": bool(int(d.get("activo", 1))),
        "orden": len(lst)+1
    }
    lst.append(item)
    return jsonify(ok=True, item=item)

@app.put("/api/conf/ventas/estado/<grupo>/<int:eid>")
@login_required
def api_estado_update(grupo, eid):
    if grupo not in ESTADOS: return jsonify(ok=False, error="Grupo inválido"), 400
    d=request.get_json(force=True) or {}
    lst = ESTADOS[grupo]
    for x in lst:
        if x["id"]==eid:
            x["nombre"]  = d.get("nombre", x["nombre"]).strip()
            x["color"]   = d.get("color", x["color"]).strip()
            x["finaliza"]= bool(int(d.get("finaliza", int(x["finaliza"]))))
            x["activo"]  = bool(int(d.get("activo", int(x["activo"]))))
            return jsonify(ok=True, item=x)
    return jsonify(ok=False, error="No encontrado"), 404

@app.delete("/api/conf/ventas/estado/<grupo>/<int:eid>")
@login_required
def api_estado_delete(grupo, eid):
    if grupo not in ESTADOS: return jsonify(ok=False, error="Grupo inválido"), 400
    lst = ESTADOS[grupo]
    pre=len(lst)
    ESTADOS[grupo] = [x for x in lst if x["id"]!=eid]
    _reorder(ESTADOS[grupo])
    if len(ESTADOS[grupo])==pre: return jsonify(ok=False, error="No encontrado"), 404
    return jsonify(ok=True)

@app.post("/api/conf/ventas/estado/<grupo>/<int:eid>/default")
@login_required
def api_estado_default(grupo, eid):
    if grupo not in ESTADOS: return jsonify(ok=False, error="Grupo inválido"), 400
    lst = ESTADOS[grupo]; found=False
    for x in lst:
        if x["id"]==eid: x["default"]=True; found=True
        else: x["default"]=False
    if not found: return jsonify(ok=False, error="No encontrado"), 404
    return jsonify(ok=True)

@app.post("/api/conf/ventas/estado/<grupo>/<int:eid>/move")
@login_required
def api_estado_move(grupo, eid):
    if grupo not in ESTADOS: return jsonify(ok=False, error="Grupo inválido"), 400
    d=request.get_json(force=True) or {}
    ok=_move(ESTADOS[grupo], eid, d.get("direction"))
    return jsonify(ok=ok)

# ---- Bodegas
@app.post("/api/conf/ventas/bodega")
@login_required
def api_bodega_create():
    d=request.get_json(force=True) or {}
    if not d.get("codigo") or not d.get("nombre"):
        return jsonify(ok=False, error="Código y nombre requeridos"), 400
    item = {
        "id": _next_id(BODEGAS),
        "codigo": d.get("codigo","").strip(),
        "nombre": d.get("nombre","").strip(),
        "tipo": (d.get("tipo") or "bodega").strip(),
        "direccion": (d.get("direccion") or "").strip(),
        "capacidad": int(d.get("capacidad") or 0),
        "responsable": (d.get("responsable") or "").strip(),
        "activo": bool(int(d.get("activo", 1))),
        "orden": len(BODEGAS)+1
    }
    BODEGAS.append(item)
    return jsonify(ok=True, item=item)

@app.put("/api/conf/ventas/bodega/<int:bid>")
@login_required
def api_bodega_update(bid):
    d=request.get_json(force=True) or {}
    for x in BODEGAS:
        if x["id"]==bid:
            x["codigo"]= d.get("codigo", x["codigo"]).strip()
            x["nombre"]= d.get("nombre", x["nombre"]).strip()
            x["tipo"]=   (d.get("tipo", x["tipo"]) or "bodega").strip()
            x["direccion"]= (d.get("direccion", x["direccion"]) or "").strip()
            x["capacidad"]= int(d.get("capacidad", x["capacidad"]))
            x["responsable"]= (d.get("responsable", x["responsable"]) or "").strip()
            x["activo"]= bool(int(d.get("activo", int(x["activo"]))))
            return jsonify(ok=True, item=x)
    return jsonify(ok=False, error="No encontrado"), 404

@app.delete("/api/conf/ventas/bodega/<int:bid>")
@login_required
def api_bodega_delete(bid):
    global BODEGAS
    pre=len(BODEGAS)
    BODEGAS=[x for x in BODEGAS if x["id"]!=bid]
    _reorder(BODEGAS)
    if len(BODEGAS)==pre: return jsonify(ok=False, error="No encontrado"), 404
    return jsonify(ok=True)

@app.post("/api/conf/ventas/bodega/<int:bid>/move")
@login_required
def api_bodega_move(bid):
    d=request.get_json(force=True) or {}
    ok=_move(BODEGAS, bid, d.get("direction"))
    return jsonify(ok=ok)



#######################################################################################

# ===== REGISTRO DE USUARIOS (wizard seguro paso a paso) =====
# Requiere: from flask import Flask, render_template, request, jsonify, redirect, url_for, session, Response  (ya está)
import re, time, secrets, datetime as _dt

# Utilidades de validación
_reserved_usernames = {"admin","root","system","ceo","soporte","autovidrios","autovidrio"}

_email_re = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
_user_re  = re.compile(r"^[a-z0-9_.-]{3,20}$")  # min 3, max 20, minúsculas + . _ -
_phone_re = re.compile(r"^(?:\+?56)?\s?9\d{8}$")  # Chile: +56 9XXXXXXXX

def _valid_email(s:str)->bool:
    return bool(_email_re.match(s or ""))

def _valid_username(s:str)->bool:
    s = (s or "").strip().lower()
    if not _user_re.match(s): return False
    if s in _reserved_usernames: return False
    if any(u == s for u in USERS.keys()): return False
    if any((x.get("username","").lower()==s) for x in USERS_DB): return False
    return True

def _valid_phone_cl(s:str)->bool:
    return bool(_phone_re.match((s or "").replace(" ","")))

def _rut_dv(num:int)->str:
    # Cálculo dígito verificador RUT Chile
    s = list(map(int, reversed(list(str(num)))))
    m = 0; f = 2
    for d in s:
        m += d*f
        f = 2 if f==7 else f+1
    r = 11 - (m % 11)
    if r == 11: return "0"
    if r == 10: return "K"
    return str(r)

def _valid_rut(rut:str)->bool:
    # Acepta formatos con puntos/guión. Valida DV.
    if not rut: return False
    s = rut.upper().replace(".","").replace("-","").strip()
    if len(s) < 2: return False
    body, dv = s[:-1], s[-1]
    if not body.isdigit(): return False
    return _rut_dv(int(body)) == dv

_common_pw = {
    "123456","12345678","qwerty","password","111111","123456789","123123","abc123",
    "000000","iloveyou","admin","autovidrios","autovidrio"
}
def _valid_password(pw:str)->tuple[bool,str]:
    pw = pw or ""
    if len(pw) < 8: return False, "Mínimo 8 caracteres."
    if pw.lower() in _common_pw: return False, "Demasiado común."
    if not re.search(r"[a-z]", pw): return False, "Debe incluir minúsculas."
    if not re.search(r"[A-Z]", pw): return False, "Debe incluir mayúsculas."
    if not re.search(r"\d", pw): return False, "Debe incluir números."
    if not re.search(r"[^\w\s]", pw): return False, "Debe incluir un símbolo."
    return True, ""

def _rate_limit_reg():
    # simple rate-limit por sesión
    k = "reg_attempts"
    now = time.time()
    window = 600  # 10 min
    session.setdefault(k, [])
    session[k] = [t for t in session[k] if now - t < window]
    if len(session[k]) >= 20:
        return False
    session[k].append(now); return True

@app.get("/registro")
def registro_view():
    # nonce anti-CSRF + temporizador mínimo
    nonce = secrets.token_urlsafe(16)
    session["reg_nonce"] = nonce
    session["reg_started_at"] = time.time()
    return render_template("registro.html", nonce=nonce)

@app.post("/api/registro/check-username")
def registro_check_username():
    if not _rate_limit_reg():
        return jsonify(ok=False, error="Demasiados intentos. Intenta más tarde."), 429
    u = (request.json or {}).get("username","").strip().lower()
    if _valid_username(u):
        return jsonify(ok=True)
    return jsonify(ok=False, error="Usuario inválido o ya existe.")

@app.post("/api/registro/check-email")
def registro_check_email():
    if not _rate_limit_reg():
        return jsonify(ok=False, error="Demasiados intentos. Intenta más tarde."), 429
    e = (request.json or {}).get("email","").strip()
    if not _valid_email(e): return jsonify(ok=False, error="Email no válido.")
    if any(x.get("email","").lower()==e.lower() for x in USERS_DB):
        return jsonify(ok=False, error="Email ya registrado.")
    return jsonify(ok=True)

@app.post("/api/registro/create")
def registro_create():
    if not _rate_limit_reg():
        return jsonify(ok=False, error="Demasiados intentos. Intenta más tarde."), 429

    data = request.get_json(force=True) or {}
    # CSRF básico
    if data.get("nonce") != session.get("reg_nonce"):
        return jsonify(ok=False, error="Token inválido. Recarga la página."), 400
    # Tiempo mínimo para evitar bots
    if time.time() - float(session.get("reg_started_at", 0)) < 3:
        return jsonify(ok=False, error="Completa el formulario con calma."), 400

    # Paso 1 - Cuenta
    username = (data.get("username") or "").strip().lower()
    email    = (data.get("email") or "").strip()
    phone    = (data.get("phone") or "").strip().replace(" ","")
    if not _valid_username(username): return jsonify(ok=False, error="Usuario inválido o existente."), 400
    if not _valid_email(email): return jsonify(ok=False, error="Email inválido."), 400
    if not _valid_phone_cl(phone): return jsonify(ok=False, error="Teléfono chileno inválido (+56 9XXXXXXXX)."), 400

    # Paso 2 - Empresa
    empresa  = (data.get("empresa") or "").strip()
    rut_emp  = (data.get("rut_empresa") or "").strip()
    rubro    = (data.get("rubro") or "").strip()
    if not empresa: return jsonify(ok=False, error="Nombre de empresa requerido."), 400
    if not _valid_rut(rut_emp): return jsonify(ok=False, error="RUT de empresa inválido."), 400

    # Paso 3 - Seguridad
    pw1 = data.get("password") or ""
    pw2 = data.get("password2") or ""
    ok, why = _valid_password(pw1)
    if not ok: return jsonify(ok=False, error=f"Contraseña débil: {why}"), 400
    if pw1 != pw2: return jsonify(ok=False, error="Las contraseñas no coinciden."), 400
    if not bool(data.get("terms")): return jsonify(ok=False, error="Debes aceptar los términos."), 400
    # Captcha simple opcional
    captcha = str(data.get("captcha") or "").strip()
    if captcha != session.get("reg_captcha",""):
        return jsonify(ok=False, error="Captcha incorrecto."), 400

    # Crear usuario
    if username in USERS:
        return jsonify(ok=False, error="El usuario ya existe."), 400

    USERS[username] = generate_password_hash(pw1)  # ya tienes importado generate_password_hash
    # Añadir a USERS_DB con rol "Cliente"
    new_id = max([u["id"] for u in USERS_DB], default=0) + 1
    USERS_DB.append({
        "id": new_id,
        "username": username,
        "email": email,
        "role": "Cliente",
        "active": True,
        "last_login": None,
        "is_system": False,
        "empresa": empresa,
        "rut_empresa": rut_emp,
        "fono": phone,
        "rubro": rubro
    })

    # Limpia nonce y captcha
    session.pop("reg_nonce", None)
    session.pop("reg_captcha", None)

    return jsonify(ok=True, message="Cuenta creada. Ya puedes iniciar sesión.", redirect=url_for("login"))


########################


# ================== RECUPERAR CONTRASEÑA ==================
from flask import render_template, request, flash

# Vista del formulario
@app.get("/recuperar")
def recuperar_view():
    return render_template("recuperar.html")

# Procesa el POST del formulario
@app.post("/recuperar")
def recuperar_post():
    email = (request.form.get("email") or "").strip().lower()

    # Simulación: validar que el email existe en la BD (USERS_DB de tu demo)
    user = next((u for u in USERS_DB if u["email"].lower() == email), None)

    if not user:
        flash("El correo no está registrado en el sistema.", "error")
        return render_template("recuperar.html")

    # Aquí en un sistema real enviarías un email con token seguro
    # Por ahora solo simulamos mensaje de éxito
    flash("Se ha enviado un enlace de recuperación a tu correo.", "success")
    return render_template("recuperar.html")

#####


# ================== PERFIL ==================
@app.get("/perfil")
def perfil():
    if "user" not in session:
        return redirect(url_for("login_view"))

    usuario = session["user"]
    datos = {
        "usuario": usuario,
        "nombre": "Juan Pérez",
        "email": f"{usuario}@empresa.cl",
        "telefono": "+56 9 9123 4567",
        "empresa": "AutoVidrios",
        "rol": "Administrador"
    }
    return render_template("perfil.html", datos=datos)

@app.post("/perfil/editar")
def perfil_editar():
    if "user" not in session:
        return redirect(url_for("login_view"))

    # Aquí actualizarías en la BD. Ejemplo de simulación:
    nombre = request.form.get("nombre")
    email = request.form.get("email")
    telefono = request.form.get("telefono")
    flash("Datos actualizados correctamente.", "success")
    return redirect(url_for("perfil"))

@app.post("/perfil/password")
def perfil_password():
    if "user" not in session:
        return redirect(url_for("login_view"))

    actual = request.form.get("actual")
    nueva = request.form.get("nueva")
    repite = request.form.get("repite")

    # Aquí deberías validar la contraseña actual y actualizar en la BD
    if nueva != repite:
        flash("Las contraseñas no coinciden.", "error")
        return redirect(url_for("perfil"))

    flash("Contraseña actualizada correctamente.", "success")
    return redirect(url_for("perfil"))

#####

@app.route("/api/config/empresa", methods=["POST"])
def save_empresa():
    data = request.form.to_dict()
    logo = request.files.get("logo")

    # aquí guardas en DB los datos de empresa
    # si quieres guardar logo: logo.save("static/uploads/logo.png")

    return jsonify(ok=True, empresa=data)


####________________________________________________________________________________

# ------------ UTILIDADES PDF PEDIDO (pegar en app.py) -----------------
from io import BytesIO
from flask import send_file, abort
import os

def _clp(n):
    try:
        return "$" + format(int(n), ",").replace(",", ".")
    except Exception:
        return str(n)

def _find_logo(app):
    """Busca static/logo.png de forma segura (opcional)."""
    try:
        p = os.path.join(app.static_folder or "static", "logo.png")
        return p if os.path.exists(p) else None
    except Exception:
        return None

def _build_pedido_pdf(app, pedido):
    # Importación perezosa para no romper el arranque si falta reportlab
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors

    W, H = A4
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)

    # ----- Encabezado (logo + empresa + número) -----
    logo = _find_logo(app)
    x_margin, y_top = 50, H - 40

    if logo:
        # Logo a la izquierda (ajusta tamaño si lo necesitas)
        c.drawImage(logo, x_margin, y_top - 50, width=60, height=50, mask="auto")

    # Marca/Nombre
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.HexColor("#0ea5e9"))
    c.drawString(x_margin + (70 if logo else 0), y_top - 15, "AUTOVIDRIOS S.A.")

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    base_x = x_margin + (70 if logo else 0)
    c.drawString(base_x, y_top - 32, "RUT: 76.123.456-7")
    c.drawString(base_x, y_top - 46, "Av. Las Torres 1234, Santiago - Chile")
    c.drawString(base_x, y_top - 60, "Tel: +56 2 2345 6789")

    # Número de pedido
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.black)
    c.drawRightString(W - x_margin, y_top - 15, f"Pedido Nº {pedido.get('numero','')}")

    # Línea separadora
    c.setStrokeColor(colors.HexColor("#0ea5e9"))
    c.setLineWidth(1)
    c.line(x_margin, y_top - 75, W - x_margin, y_top - 75)

    # ----- Datos del cliente -----
    y = y_top - 105
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_margin, y, "Datos del Cliente")
    c.setFont("Helvetica", 11)
    y -= 18
    c.drawString(x_margin, y, f"Cliente: {pedido.get('cliente','')}")
    y -= 15
    c.drawString(x_margin, y, f"Cotización: #{pedido.get('cotizacion_id','')}")
    y -= 15
    c.drawString(x_margin, y, f"Fecha: {pedido.get('fecha','')}")
    y -= 15
    c.drawString(x_margin, y, f"Entrega: {pedido.get('fecha_entrega','')}")
    y -= 15
    c.drawString(x_margin, y, f"Condición de pago: {pedido.get('cond_pago','')}")

    # ----- Detalle (tabla) -----
    y -= 35
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor("#0ea5e9"))
    c.drawString(x_margin, y, "Detalle del Pedido")
    c.setFillColor(colors.black)

    # Encabezado de tabla
    y -= 25
    c.setFillColor(colors.HexColor("#0ea5e9"))
    c.rect(x_margin, y - 5, W - 2*x_margin, 20, fill=1, stroke=0)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x_margin + 10, y, "Cant.")
    c.drawString(x_margin + 70, y, "Descripción")
    c.drawRightString(W - x_margin - 120, y, "P. Unitario")
    c.drawRightString(W - x_margin - 10, y, "Subtotal")

    # Filas
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 11)
    y -= 25
    total = 0
    items = pedido.get("items", []) or []
    for it in items:
        cant = it.get("cantidad", 0)
        desc = it.get("descripcion", "")
        precio = it.get("precio", 0)
        sub = int(cant) * int(precio)
        total += sub

        c.drawString(x_margin + 10, y, str(cant))
        c.drawString(x_margin + 70, y, desc)
        c.drawRightString(W - x_margin - 120, y, _clp(precio))
        c.drawRightString(W - x_margin - 10, y, _clp(sub))
        y -= 20

    # Total
    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(W - x_margin - 120, y, "TOTAL:")
    c.setFillColor(colors.HexColor("#22c55e"))
    c.drawRightString(W - x_margin - 10, y, _clp(total))

    # Footer
    c.setFillColor(colors.HexColor("#6b7280"))
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(W / 2, 40, "Gracias por su preferencia - AUTOVIDRIOS S.A.")

    c.showPage()
    c.save()
    buf.seek(0)
    return buf

# ---- ENDPOINT SEGURO: /pedidos/<numero>/pdf ----
# No reemplaza tu vista de /pedidos : solo añade el PDF.
@app.get("/pedidos/<int:numero>/pdf")
def pedidos_pdf(numero):
    """
    Obtiene el pedido y devuelve un PDF.
    Integra con tu capa real de datos. Aquí hay 3 formas de obtenerlo:
    1) Si ya tienes una función global get_pedido(numero) úsala.
    2) Si tienes una lista PEDIDOS en memoria, se intenta buscar ahí.
    3) Fallback de ejemplo si no existe nada (no interfiere con tu app).
    """
    # 1) Función existente
    pedido = None
    if 'get_pedido' in globals() and callable(globals()['get_pedido']):
        try:
            pedido = globals()['get_pedido'](numero)
        except Exception:
            pedido = None

    # 2) Lista existente PEDIDOS
    if pedido is None and 'PEDIDOS' in globals():
        try:
            pedido = next((p for p in PEDIDOS if int(p.get("numero")) == int(numero)), None)
        except Exception:
            pedido = None

    # 3) Fallback (solo para no romper si no tienes nada conectado)
    if pedido is None:
        pedido = {
            "numero": numero,
            "cotizacion_id": 100 + numero,
            "cliente": "Cliente de ejemplo",
            "fecha": "2025-09-14",
            "fecha_entrega": "2025-09-20",
            "cond_pago": "30 días",
            "items": [
                {"cantidad": 2, "descripcion": "Vidrio templado lateral", "precio": 50000},
                {"cantidad": 1, "descripcion": "Instalación completa", "precio": 54690},
            ],
        }

    if not pedido:
        abort(404)

    pdf = _build_pedido_pdf(app, pedido)
    return send_file(pdf,
                     as_attachment=True,
                     download_name=f"pedido_{numero}.pdf",
                     mimetype="application/pdf")
# ------------ /UTILIDADES PDF PEDIDO -----------------------------------



###############________________________________

from flask import request, render_template, send_file, abort
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

@app.get("/articulo/<int:art_id>/pdf")
def articulo_pdf(art_id):
    a = get_articulo_by_id(art_id)
    if not a:
        abort(404)

    # v=old -> ReportLab (tu PDF clásico)
    if request.args.get("v") == "old":
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica-Bold", 18)
        c.drawString(2*cm, height - 2*cm, "Ficha Técnica")
        c.setFont("Helvetica", 12)
        c.drawString(2*cm, height - 2.7*cm, a.get("descripcion",""))

        if a.get("imagenes"):
            try:
                c.drawImage("." + a["imagenes"][0], 2*cm, height - 10*cm,
                            width=10*cm, height=6*cm, preserveAspectRatio=True, mask='auto')
            except Exception:
                c.setFillColor(colors.red)
                c.drawString(2*cm, height - 10*cm, "[Imagen no disponible]")

        y = height - 11*cm
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2*cm, y, "Datos principales")
        c.setFont("Helvetica", 11)
        y -= 0.6*cm
        datos = [
            ("Código", a.get("cod_int","-")),
            ("Categoría", a.get("categoria","-")),
            ("Marca", a.get("marca","-")),
            ("Modelo", a.get("modelo","-")),
            ("Año", a.get("anio","-")),
            ("Estado", a.get("estado","-")),
            ("Precio neto", f"${(a.get('precio_venta') or 0):,}".replace(",", "."))
        ]
        for label, val in datos:
            c.drawString(2*cm, y, f"{label}: {val}")
            y -= 0.5*cm

        c.setFont("Helvetica-Oblique", 9)
        c.setFillColor(colors.gray)
        c.drawString(2*cm, 1.5*cm, "Generado automáticamente por Autovidrios · Software a medida")

        c.showPage(); c.save(); buf.seek(0)
        return send_file(buf, mimetype="application/pdf", as_attachment=False,
                         download_name=f"ficha_{a.get('cod_int','art')}.pdf")

    # Por defecto -> NUEVO diseño (HTML). Si hay WeasyPrint, lo convierte a PDF.
    html = render_template("pdf/ficha_tecnica.html", a=a, empresa_nombre="AutoVidrios")
    try:
        from weasyprint import HTML
        pdf = HTML(string=html, base_url=request.host_url).write_pdf()
        return send_file(io.BytesIO(pdf), mimetype="application/pdf", as_attachment=False,
                         download_name=f"ficha_{a.get('cod_int','art')}.pdf")
    except Exception:
        # fallback: muestra HTML si no tienes convertidor instalado
        return html


    # buffer para PDF
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    # ======= CABECERA =======
    c.setFont("Helvetica-Bold", 18)
    c.drawString(2*cm, height - 2*cm, "Ficha Técnica")
    c.setFont("Helvetica", 12)
    c.drawString(2*cm, height - 2.7*cm, art["descripcion"])

    # ======= IMAGEN =======
    if art.get("imagenes"):
        try:
            c.drawImage("." + art["imagenes"][0], 2*cm, height - 10*cm, width=10*cm, height=6*cm, preserveAspectRatio=True, mask='auto')
        except:
            c.setFillColor(colors.red)
            c.drawString(2*cm, height - 10*cm, "[Imagen no disponible]")

    # ======= DATOS PRINCIPALES =======
    y = height - 11*cm
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, y, "Datos principales")
    c.setFont("Helvetica", 11)
    y -= 0.6*cm
    datos = [
        ("Código", art["cod_int"]),
        ("Categoría", art.get("categoria", "-")),
        ("Marca", art.get("marca", "-")),
        ("Modelo", art.get("modelo", "-")),
        ("Año", art.get("anio", "-")),
        ("Estado", art.get("estado", "-")),
        ("Precio neto", f"${art.get('precio_venta', 0):,}".replace(",", "."))
    ]
    for label, val in datos:
        c.drawString(2*cm, y, f"{label}: {val}")
        y -= 0.5*cm

    # ======= PIE DE PÁGINA =======
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(colors.gray)
    c.drawString(2*cm, 1.5*cm, "Generado automáticamente por Autovidrios · Software a medida")

    c.showPage()
    c.save()

    buf.seek(0)
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name=f"ficha_{art['cod_int']}.pdf")



# ================== COTIZACIONES -> PDF ==================
from io import BytesIO
from flask import send_file, jsonify, url_for
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import os

@app.get("/cotizaciones/pdf/<int:cid>")
@login_required
def cotizacion_pdf(cid):
    # Busca la cotización
    c = next((x for x in COTIZACIONES if x["id"] == cid), None)
    if not c:
        return "Cotización no encontrada", 404

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=60, bottomMargin=40)
    styles = getSampleStyleSheet()
    elements = []

    # ===== Encabezado =====
    elements.append(Paragraph("<b>AUTOVIDRIOS</b>", styles["Title"]))
    elements.append(Paragraph("Dirección · Teléfono · Email", styles["Normal"]))
    elements.append(Spacer(1, 12))

    info = f"""
    <b>COTIZACIÓN Nº {c['id']}</b><br/>
    Cliente: {c['cliente']}<br/>
    Fecha: {c['fecha']}<br/>
    Estado: {c['estado']}
    """
    elements.append(Paragraph(info, styles["Normal"]))
    elements.append(Spacer(1, 20))

    # ===== Tabla de Items =====
    data = [["Foto", "Descripción", "Cantidad", "Precio Neto", "Descuento", "Total"]]
    for item in c.get("items", []):
        # Miniatura de imagen
        foto = ""
        if item.get("imagen"):
            try:
                foto = Image(item["imagen"], width=40, height=40)
            except:
                foto = ""
        row = [
            foto,
            item.get("descripcion", ""),
            str(item.get("cantidad", 0)),
            f"${item.get('precio',0):,.0f}".replace(",", "."),
            f"{item.get('descuento',0)}%",
            f"${item.get('total',0):,.0f}".replace(",", "."),
        ]
        data.append(row)

    table = Table(data, colWidths=[50, 200, 50, 70, 70, 70])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0ea5e9")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("ALIGN", (2,1), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 10),
    ]))
    elements.append(table)

    # ===== Totales =====
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"<b>Subtotal:</b> ${c.get('subtotal', c['total']):,.0f}".replace(",", "."), styles["Normal"]))
    elements.append(Paragraph(f"<b>Descuento:</b> ${c.get('descuento_total', 0):,.0f}".replace(",", "."), styles["Normal"]))
    elements.append(Paragraph(f"<b>IVA:</b> ${c.get('iva', 0):,.0f}".replace(",", "."), styles["Normal"]))
    elements.append(Paragraph(f"<b>TOTAL:</b> ${c['total']:,.0f}".replace(",", "."), styles["Heading2"]))

    # ===== Footer legal =====
    elements.append(Spacer(1, 30))
    footer = """
    <i>El stock y los precios deben ser confirmados por un vendedor autorizado de Autovidrios.<br/>
    Esta cotización es solo referencial y no constituye un compromiso de venta.</i>
    """
    elements.append(Paragraph(footer, styles["Normal"]))

    # Construir documento
    doc.build(elements)
    buf.seek(0)

    return send_file(buf, as_attachment=True,
                     download_name=f"cotizacion_{cid}.pdf",
                     mimetype="application/pdf")




####



# === MARKETPLACE funcional ===
import os, json
from flask import render_template, request, jsonify, redirect, url_for

APPS_PATH = os.path.join("ai_store", "apps.json")
INSTALLS_PATH = os.path.join("ai_store", "installs.json")

DEFAULT_APPS = [
    {"slug":"clientes","nombre":"Clientes","categoria":"ERP","descargas":512,
     "descripcion":"Gestión de clientes y contactos.","icono":"/static/sprites/clientes.svg"},
    {"slug":"inventario","nombre":"Inventario","categoria":"Logística","descargas":534,
     "descripcion":"SKUs, lotes, bodegas y códigos.","icono":"/static/sprites/inventario.svg"},
    {"slug":"ventas","nombre":"Ventas","categoria":"ERP","descargas":501,
     "descripcion":"Cotizaciones, pedidos y documentos.","icono":"/static/sprites/ventas.svg"}
]

def _load_apps():
    try:
        os.makedirs(os.path.dirname(APPS_PATH), exist_ok=True)
        if os.path.exists(APPS_PATH):
            with open(APPS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return DEFAULT_APPS

def _load_installs():
    if not os.path.exists(INSTALLS_PATH):
        return {}
    with open(INSTALLS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_installs(data: dict):
    os.makedirs(os.path.dirname(INSTALLS_PATH), exist_ok=True)
    with open(INSTALLS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _empresa_id():
    # Ajusta si usas sesión de empresa
    # from flask import session; return str(session.get("empresa_activa_id","default"))
    return "default"

# Exponer helper a los templates (para ocultar/mostrar menú)
@app.context_processor
def _inject_install_helpers():
    eid = _empresa_id()
    installed = set(_load_installs().get(eid, []))
    def is_installed(slug): return slug in installed
    return dict(is_installed=is_installed, installed_modules=installed)

# Catálogo UI
@app.get("/marketplace")
def marketplace_home():
    q   = request.args.get("q","").strip().lower()
    cat = request.args.get("cat","").strip().lower()
    apps = _load_apps()
    if q:
        apps = [a for a in apps if q in a["nombre"].lower() or q in a.get("descripcion","").lower()]
    if cat:
        apps = [a for a in apps if cat == a.get("categoria","").lower()]
    inst = set(_load_installs().get(_empresa_id(), []))
    for a in apps:
        a["instalada"] = a["slug"] in inst
    cats = sorted({a.get("categoria","General") for a in _load_apps()})
    return render_template("marketplace.html", apps=apps, cats=cats, q=q, cat=cat)

# Instalar / desinstalar
@app.post("/marketplace/toggle/<slug>")
def marketplace_toggle(slug):
    eid = _empresa_id()
    data = _load_installs()
    current = set(data.get(eid, []))
    if slug in current:
        current.remove(slug); estado = "desinstalada"
    else:
        current.add(slug);    estado = "instalada"
    data[eid] = sorted(list(current))
    _save_installs(data)
    return jsonify({"ok": True, "slug": slug, "estado": estado})

# Gatekeeper: bloquea rutas de módulos no instalados
PROTECTED_PREFIX = {
    "clientes":   ["/clientes"],
    "inventario": ["/inventario"],
    "ventas":     ["/cotizaciones", "/pedidos", "/ventas"]
}
@app.before_request
def _gate_modules():
    path = request.path
    if path.startswith(("/marketplace","/static")):
        return
    eid = _empresa_id()
    installed = set(_load_installs().get(eid, []))
    for slug, prefixes in PROTECTED_PREFIX.items():
        if slug not in installed and any(path.startswith(p) for p in prefixes):
            return redirect(url_for("marketplace_home"))

