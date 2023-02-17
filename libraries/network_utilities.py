import socket, pickle

class NetworkUtilities():
    def _create_client(self, host, port):
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        trying = True 

        while trying:
            try: 
                c.connect((host, port))
                trying = False
            except:
                continue 

        print("[INFO] connected to...{} on {}".format(host, port)) 
        
        return c 

    def _create_server(self, port): 
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        s.bind(("", port)) 
        s.listen(10) 
        conn, addr = s.accept() 
        print("[INFO] connected to...{}".format(addr)) 
        
        return conn
    
    def _send_list(self, vs, lst):
        data = pickle.dumps(lst)
        vs.sendall(data)
        
    def _receive_list(self, conn):
        data = conn.recv(1024)
        lst = pickle.loads(data)
        
        return lst
    
    def _destroy(self, s):
        s.shutdown(1)
        s.close()