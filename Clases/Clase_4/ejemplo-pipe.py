from multiprocessing import Process, Pipe

def productor(conn):
    datos = ["manzana", "banana", "durazno"]
    for item in datos:
        conn.send(item)
    conn.send("FIN")
    conn.close()

def filtro(conn_in, conn_out):
    while True:
        item = conn_in.recv()
        if item == "FIN":
            break
        if "a" in item:
            conn_out.send(item.upper())
    conn_out.send("FIN")
    conn_in.close()
    conn_out.close()

def consumidor(conn):
    while True:
        item = conn.recv()
        if item == "FIN":
            break
        print("Consumidor recibió:", item)
    conn.close()

if __name__ == "__main__":
    p1_conn, f1_conn = Pipe()
    f2_conn, c_conn = Pipe()

    p1 = Process(target=productor, args=(p1_conn,))
    f1 = Process(target=filtro, args=(f1_conn, f2_conn))
    c1 = Process(target=consumidor, args=(c_conn,))

    p1.start()
    f1.start()
    c1.start()

    p1.join()
    f1.join()
    c1.join()