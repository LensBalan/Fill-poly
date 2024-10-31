import tkinter as tk  #Interface grafica
from tkinter import colorchooser
import math  

class Tela_de_Desenho:
    def __init__(self, root):#self construtor
        self.root = root

    #------------------------------- TELA DE DESENHO E MENU --------------------------------

        self.root.title("Fill Poly")
        self.label = tk.Label(root, text="Fill Poly", font=("Helvetica", 16)) #"Fill Poly"
        self.label.pack(pady=10)
        self.canvas_width = 640  #640 x 480
        self.canvas_height = 480
        
        self.frame = tk.Frame(root) #Frame para desenho
        self.frame.pack()
        
        self.canvas = tk.Canvas(self.frame, width=self.canvas_width + 40, height=self.canvas_height + 40, bg="gray")
        self.canvas.pack() # + 40 para os eixos x e y
        
        #Retangulo de desenho (branco)
        self.canvas.create_rectangle(20, 20, self.canvas_width + 20, self.canvas_height + 20, fill="white", outline="black")
        self.Desenha_xy() # eixos x e y

        self.vertices = [] #Lista de vertices (x, y)
        self.poligonos = []  #Poligonos armazenados (vertices, cor_preenchimento)
        self.indice_poli = 0  #Começa com zero
        self.matriz_poligonos = [[-1 for _ in range(self.canvas_width)] for _ in range(self.canvas_height)] #matriz 640x480 para seleçao de poligonos
        self.indice_selecionado = -1

        #Cores Padrao (Arestas e preenchimento)
        self.cor_aresta = "yellow" 
        self.cor_preenchimento = "green" 

        #Cliques do mouse (desenhar V e fechar poligono)
        self.canvas.bind("<Button-1>", self.Desenha_ponto)
        self.canvas.bind("<Button-3>", self.Fecha_poligono) 

        #Menu de options
        self.Cria_menu()

    def Cria_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        color_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Opções", menu=color_menu) #Opçoes:
        color_menu.add_command(label="Alterar Cor das Arestas", command=self.Trocar_cor_arestas)
        color_menu.add_command(label="Alterar Cor de Preenchimento", command=self.Trocar_cor_preenchimento)
        color_menu.add_command(label="Limpar Tela", command=self.Limpar_tela)
        color_menu.add_command(label="Selecionar Polígono", command=self.Ativar_modo_selecao)
        color_menu.add_command(label="Voltar ao Modo de Desenho", command=self.Ativar_modo_desenho)

        poligono_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Polígono Selecionado", menu=poligono_menu)
        poligono_menu.add_command(label="Excluir Polígono Selecionado", command=self.Excluir_poligono_selecionado)
        poligono_menu.add_command(label="Alterar Cor do Polígono Selecionado", command=self.Trocar_cor_poligono_selecionado)

   #------------------------------------FUNÇÕES----------------------------------------
   
    def Desenha_xy(self): #Coloca o eixo x e y fora da area de desenho
        self.canvas.create_line(20, self.canvas_height + 20, self.canvas_width + 20, self.canvas_height + 20, arrow=tk.LAST)
        self.canvas.create_line(20, 20, 20, self.canvas_height + 20, arrow=tk.LAST)

    def Desenha_ponto(self, event):
        x = event.x - 20 # -20 para compensar o espaço extra dos eixos
        y = event.y - 20

        #Clique dentro da area de desenho?
        if 0 <= x <= self.canvas_width and 0 <= y <= self.canvas_height:
            self.vertices.append((x, y)) #Add lista de vertices

            print(f"Coordenadas: ({x}, {y})")
            print(f"Lista de vértices: {self.vertices}")

            #Desenha um circulo de raio r(ponto)
            r = 1
            self.canvas.create_oval(event.x - r, event.y - r, event.x + r, event.y + r, fill="black")

            #Traça aresta de um ponto a outro, se ja houver + de 1
            if len(self.vertices) > 1:
                x1, y1 = self.vertices[-2]
                x2, y2 = self.vertices[-1]
                self.canvas.create_line(x1 + 20, y1 + 20, x2 + 20, y2 + 20, fill=self.cor_aresta) #aresta

    def Fecha_poligono(self, event):
        #Um poligono deve ter + de 3 vertices
        if len(self.vertices) > 2:  
            x1, y1 = self.vertices[-1] #Conecta o ultimo vertice com o primeiro
            x2, y2 = self.vertices[0]
            self.canvas.create_line(x1 + 20, y1 + 20, x2 + 20, y2 + 20, fill=self.cor_aresta)
            print(f"Polígono fechado com os vértices: {self.vertices}")

            self.Fill_poly_func()  #Apos fechar, preenche
            self.Salvar_poligono()  #Salva na lista de poligonos
            self.vertices.clear() #Reseta a lista de vertices
        else:
            print("Polígono não fechado, menos de 3 pontos.")
   
    def Trocar_cor_arestas(self):
        color = colorchooser.askcolor(title="Escolha a Cor das Arestas")  #seletor de cores
        if color[1] is not None:  #se uma cor foi escolhida, troca
            self.cor_aresta = color[1]
            print(f"Cor das arestas alterada para: {self.cor_aresta}")

    def Trocar_cor_preenchimento(self):
        color = colorchooser.askcolor(title="Escolha a Cor de Preenchimento")
        if color[1] is not None:
            self.cor_preenchimento = color[1]
            print(f"Cor de preenchimento alterada para: {self.cor_preenchimento}")
    
    # Funcao Fill poly
    def Fill_poly_func(self):
    #Encontrar os valores min e max de y (scan lines a serem processadas)
        ymin = min(v[1] for v in self.vertices)
        ymax = max(v[1] for v in self.vertices)
       
        print(f"ymin: {ymin}, ymax: {ymax}")

        #Lista de interceçoes (Inicialaze) Ns = ymax - ymin (+1 processar ymax tbm)
        scan_lines = [[] for _ in range(ymax - ymin +1)]

         #Processando todas as arestas, seq 
        for i in range(len(self.vertices)):
            v1 = self.vertices[i]
            v2 = self.vertices[(i + 1) % len(self.vertices)]  #Conecta ao prox vertice

            #x e y dos V a serem processados
            x1, y1 = v1 
            x2, y2 = v2

            #Ignora arestas horizontais
            if y1 != y2:
                if y1 > y2:  #(y1, x1) é sempre o menor
                    x1, y1, x2, y2 = x2, y2, x1, y1

                dx = x2 - x1
                dy = y2 - y1
                Tx = dx / dy  # Taxa de variacao em x (incremento)

                #x atual
                x_n = x1
               #y_n = y1 y incrementa em 1

                print(f"Processando aresta de ({x1}, {y1}) para ({x2}, {y2})")

                #Processa cada scan line de forma inc (y_n += 1)
                for y in range(y1, y2):
                    scan_lines[y - ymin].append(x_n) #armazena intersecao
                    print(f"Scan line {y}: x = {x_n}")
                
                    x_n += Tx #Proxima SL, inc com a taxa(var. horizontal por linha)

        #Preenchimento entre interseçoes
        for y in range(len(scan_lines)):
            if scan_lines[y]:  #Se houver interçoes
                scan_lines[y].sort()  #Ordena as interseçoes
                print(f"Preenchendo scan line {y + ymin} com interseções em x: {scan_lines[y]}")
                for i in range(0, len(scan_lines[y]), 2):  #Preenche entre pares de interseçoes
                    x_ini = max(0, math.ceil(scan_lines[y][i]))#de x_ini (ceil)
                    x_fim = min(self.canvas_width, math.floor(scan_lines[y][i + 1]))#ate x_fim (floor)

                    #Atualiza a matriz com o indice_poli
                    for x in range(x_ini, x_fim + 1):
                        if 0 <= x < self.canvas_width and 0 <= (y + ymin) < self.canvas_height:
                            self.matriz_poligonos[y + ymin][x] = self.indice_poli

                    print(f"Desenhando linha de x_ini = {x_ini} até x_fim = {x_fim} na scan line {y + ymin}")
                    self.canvas.create_line(x_ini + 20, y + ymin + 20, x_fim + 20, y + ymin + 20, fill=self.cor_preenchimento) #+20 compensaçao

    def Salvar_poligono(self):
        if self.vertices:
            self.poligonos.append((self.indice_poli,self.vertices.copy(), self.cor_preenchimento))#add a lista de poligonos
            print(f"Polígono salvo: {self.poligonos[-1]}")
            print(f"Lista de polígonos: {self.poligonos}") 
            self.indice_poli += 1 #inc indice do poligono

    def Limpar_tela(self):
        #Limpa todos os poligonos e a area de desenho
        self.canvas.delete("all")
        self.canvas.create_rectangle(20, 20, self.canvas_width + 20, self.canvas_height + 20, fill="white", outline="black")
        self.Desenha_xy()  #Redesenha os eixos
        self.vertices.clear()  #Limpa a lista de V
        self.poligonos.clear()  #Limpa a lista de poligonos
        #Reinicializa a matriz de poligonos
        self.matriz_poligonos = [[-1 for _ in range(self.canvas_width)] for _ in range(self.canvas_height)]
        self.indice_poli = 0
        print("Área de desenho limpa.")

    def Ativar_modo_selecao(self):
        self.canvas.bind("<Button-1>", self.Seleciona_poligono)
        print("Modo de Seleção ativado.")
    
    def Ativar_modo_desenho(self):
        self.canvas.bind("<Button-1>", self.Desenha_ponto)
        print("Modo de Desenho ativado.")

    def Seleciona_poligono(self, event):
        x = event.x - 20  #Compensar o espaço extra dos eixos
        y = event.y - 20

        #Verifica se o clique ta dentro da area de desenho
        if 0 <= x < self.canvas_width and 0 <= y < self.canvas_height:
            indice_poli = self.matriz_poligonos[y][x]
            if indice_poli != -1: # -1: nenhum poligono
                self.indice_selecionado = indice_poli
                print(f"Polígono {self.indice_selecionado} selecionado.")
            else:
                self.indice_selecionado = indice_poli
                print("Nenhum polígono encontrado nessa posição.")

    def Trocar_cor_poligono_selecionado(self):
        #salva a cor de preenchimento anterior
        self.cor_preenchimento_anterior = self.cor_preenchimento
        #Tem poligono selecionado?
        if self.indice_selecionado != -1:
            #Solicita nova cor
            color1 = colorchooser.askcolor(title="Escolha a Nova Cor do Polígono") 
            if color1[1] is not None:  #Se uma cor foi escolhida
                #Atualiza a cor do poligono selecionado
                self.poligonos[self.indice_selecionado] = (self.poligonos[self.indice_selecionado][0], self.poligonos[self.indice_selecionado][1], color1[1])
                print(f"Cor do polígono {self.indice_selecionado} alterada para: {color1[1]}")
                self.Redesenhar_poligonos()  #Chama a func de redesenho
                self.indice_selecionado = -1
                self.cor_preenchimento = self.cor_preenchimento_anterior # retorna a cor anterior
        else:
            print("Nenhum polígono selecionado.")

    def Excluir_poligono_selecionado(self):
        #Verifica se ha um poligono selecionado
        if self.indice_selecionado != -1:
            #Remove o poligono da lista
            del self.poligonos[self.indice_selecionado]
            print(f"Polígono {self.indice_selecionado} deletado.")
            self.Redesenhar_poligonos()  #Chama a func de redesenho
            self.indice_selecionado = -1
        else:
            print("Nenhum polígono selecionado para deletar.")

    def Redesenhar_poligonos(self):
        #Armazena as infos atuais dos poligonos em uma lista temp
        poligonos_temp = self.poligonos.copy()

        self.Limpar_tela()  #Limpa a tela antes de redesenhar

        #Redesenha todos os poligonos
        for indice, (indice_poli, vertices, cor_preenchimento) in enumerate(poligonos_temp):
            self.vertices = vertices
            self.cor_preenchimento = cor_preenchimento
            self.Fecha_poligono(None)  #Chama a func de fechamento de poligono para redesenhar   

#------------------------------------------MAIN--------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = Tela_de_Desenho(root)
    root.mainloop()
