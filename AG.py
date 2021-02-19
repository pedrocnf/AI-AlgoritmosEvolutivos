############################################################
#ALGORITMO GENETICO DESENVOLVIDO PARA DISCIPLINA INTELIGENCIA ARTIFICIAL	#
#OBJETIVO: SOLUCAO EFICIENTE PARA O PROBLEMA DE ROTEAMENTO DE VEICULOS     #
#AUTOR: CESAR TINUM ,SABRINE HENRIQUE			  DATA:06-11-2009     						    #
#CENTRO UNIVERSITARIO DE BELO HORIZONTE DCE -       7 PERIODO MANHA                  #
#CONTATO : 				magodoschatsbh@gmail.com , sabrine@2xt.com.br									#
############################################################


#SELECAO     #MUTACAO   #CROSSOVER
import random											#GERACAO NUMEROS ALEATORIOS
from threading import Thread					#BIBLIOTECA DE GERACAO DE SUBPROCESSOS (THREADS)
from math import ceil								#BIBLIOTECA DE ARREDONDAMENTO NUMERICO
from time import time, strftime
class AG:
	def __init__(self, mutacao,crossover,tamPopulacao,fitnes, cidades, maxdistancia, geracoes, numthreads, naoalcanco):
		start = time()
		self.MAX_DIST = maxdistancia
		self.mutacao = mutacao 							#propriedade de mutacao
		self.crossover = crossover
		self.NAOALCANCO = naoalcanco				#possibilidade de nao haver caminho entre cidades
		self.tamPopulacao = tamPopulacao 			#numero populacao inicial
		self.fitnes = fitnes									#funcao de avaliacao
		self.populacao = []									#vetor contendo a populacao
		self.fitPopulacao = []								#vetor com resultado avaliacao de cada elem da populacao
		self.distancia = {}
		self.NUM_THREADS = numthreads
		self.geracoes = geracoes
		self. cidades = cidades
		self.disCidades(cidades)
		self.populacaoInicial = []
		self.__initGeracao()
		self.selecao()
		self.populacaoInicial = self.populacao
		for i in range(self.geracoes):
			self.__nextGeracao()
			self.__crossover()
		self.selecao()
		finish = time()
		self.time = finish - start
		self.__header()
	#FIM CLASSE INICIALIZACAO
	def __initGeracao(self):
		try:
			threads = []
			for i in range(self.NUM_THREADS):
				threads.append(self.__startThreads('self.geraPopulacao', {}))											#DISPARANDO THREADS PARA GERAR POPULACAO E AVALIACAO DOS ELEMENTOS
			self.__endThreads(threads)																											#ESPERA THREADS ACABAREM
		except Exception, e:
			print e
	def __nextGeracao(self):
		try:
			threads = []
			tamMutacao = round(ceil(float(self.tamPopulacao) / 2)* self.mutacao)														#NUMERO DE INDIVIDUOS QUE SOFRERAO MUTACAO
			faixa = int(ceil(tamMutacao / self.NUM_THREADS))
			r = int((tamMutacao>self.NUM_THREADS and self.NUM_THREADS or tamMutacao))                     #VERIFICA SE NUM THREADS E MAIOR QUE NUM ELEMENTOS QUE SOFRERAO MUTACAO
			for i in range(r):
				threads.append(self.__startThreads('self.geraMutacao', {'ini':i+1, 'tam':faixa}))				#DISPARANDO THREADS PARA EFETUAR MUTACAO NOS PIORES ELEMENTOS DA POPULACAO EM FAIXAS
			self.__endThreads(threads)																												#ESPERA THREADS ACABAREM
		except Exception, e:
			print e
	def __endThreads(self, threads):
		for t in threads:
			t.join(10)
		return
		
	def geraMutacao(self,ini,  tam):
		try:
			sorteados = []																												#GUARDA ELEMENTOS SORTEADOS PARA QUE O ALGORITMO NAO ENTRE EM LOOP SORTEANDO SEMPRE O MESMO NODO
			tamC = self.tamPopulacao
			ini = tamC - (2*ini)
			flag = True
			limite = ini + tam
			numCidades = len(self.cidades)
			while ini <= limite:
				tenhoCidades = True
				if flag:
					cont = 0
					posCorte = random.randint(3, numCidades -1)																							#PONTO DE CORTE PARA MUTACAO ALEATORIO
					n = numCidades-posCorte																															#NUMERO DE ELEMENTOS QUE SERAO TROCADOS
					list = self.populacao[ini][2:posCorte]
					del self.populacao[ini][posCorte:]																													#DELETO O RESTO DO VETOR A PARTIR DO PONTO DE CORTE PARA INSERIR NOVOS ELEMENTOS
					sorteados = []
					i = 0
					j = 0
				while tenhoCidades:
					flag = False
					nodo = self.cidades[random.randint(0, numCidades-1)]
					if  cont > numCidades - 1:
						flag = True
						break
					if nodo in sorteados or nodo in list:
						cont+=1
						continue
					try:
						if self.populacao[ini][posCorte - 1]:
							d = (self.adjacencia(nodo, self.populacao[ini][posCorte-1])  and True or None)
						else:
							d = True
					except Exception, e:
						d = None
					if d:
						self.populacao[ini].append(nodo)
						list.append(nodo)
						res = self.geraFitnes(self.populacao[ini], 2)
						self.populacao[ini][0] = res[0]
						self.populacao[ini][1] = res[1]
						i+=1
					tenhoCidades = not self.__sublist(list, self.cidades)
				if not flag:
					ini+=1
			return True
		except Exception, e:
			return False
	def __startThreads(self, funcAlvo, k):
		try:
			t = Thread(target = eval(funcAlvo), kwargs = k)
			t.start()
			return t
		except Exception, e:
			print  e
	def disCidades(self, cidades):																					#GERA DISTANCIA ENTRE CIDADES , MATRIZ DE ADJACENCIA
		for i in cidades:
			self.distancia[i] = {}
			for j in cidades:
				if  not self.distancia[i].has_key(j): 																	#SE J NAO ESTA NO DICIONARIO DA CIDADE I VOU INCLUI-LA
					if self.distancia.has_key(j) and j!=i:																#SE CIDADE J ESTA NO DICIONARIO (JA TENHO VALOR) E J!=I (NAO E A MESMA CIDADE)
						self.distancia[i][j] = self.distancia[j][i]
						continue
					if i == j:
						self.distancia[i][j] = 0
						continue
					alcanco = random.randint(1, self.NAOALCANCO)					#CHANCE DE CIDADES NAO SE ALCANCAREM = 1 EM NAO ALCANCO (PARAMETRO)
					if alcanco == 1:
						self.distancia[i][j] = 100000												#ATRIBUI VALOR DISTANCIA MUITO ALTO = CIDADE NAO ALCANCAVEL
						continue
					self.distancia[i][j] = random.randint(1, self.MAX_DIST)	#SORTEIA VALOR DA DISTANCIA ALEATORIAMENTE ENTRE 1 - MAX_DIST SE FOR A MESMA CIDADE VALOR DISTANCIA 0
		return 
	def selecao(self):																										#DIVIDIR A POPULACAO EM GRUPOS PARA APLICAR FUNCAO DE AVALIACAO POR THREADS.
		self.populacao.sort()
	def geraPopulacao(self):
		tam = int(ceil(float(self.tamPopulacao)/4))
		try:
			for i in range(tam):
				d = []
				sorteados = []
				d.append(self.cidades[random.randint(0, len(self.cidades) - 1)])																																					#1 CIDADE ALEATORIA
				sorteados.append(d[0])
				cont = 1
				while not self.__sublist(d, self.cidades):																																#RODA LOOP ENQUANTO NAO TEM TODAS CIDADES NA ROTA - SE IMPASSE ATE 100 ITERACOES - COMECA DE NOVO
					b = self.cidades[random.randint(0, len(self.cidades) - 1)]
					cont+=1
					if cont >len(self.cidades):
						cont = 0
						d = []
						sorteados = []
						d.append(self.cidades[random.randint(0, len(self.cidades) - 1)])																																					#1 CIDADE ALEATORIA
						sorteados.append(d[0])
					elif b in sorteados:
						continue
					sorteados.append(b)
					c = (self.adjacencia(d[len(d)-1],b) and d.append(b) or False)																#VERIFICA SE CIDADES SAO ADJACENTES (EXISTE ROTA ENTRE ELAS)
				if len(self.populacao) == self.tamPopulacao:																							#COMO AS THREADS PODEM SE DIVIDIR EM MAIS ELEMENTOS QUE O TAMANHO ORIGINAL PRAMETRIZADO
					return False																																			#DEVIDO AO ARREDONDAMENTO DE VEZES PARA CADA THREAD CRIAR ELEMENTOS
				res = self.geraFitnes(d, 0)																														#VERIFICO AQUI SE TAMANHO TOTAL DE ELEMENTOS JA FOI CRIADO ANTES SE INSERIR CADA ELEMENTO
				d.insert(0, res[0])
				d.insert(1, res[1])
				self.populacao.append(d)
			return True
		except Exception, e:
			print e

	def adjacencia(self, a, b):
		return ((self.distancia[a][b]<9999 and a!=b or False) and True or False)            #SE A DISTANCIA MENOR QUE 9999 AVALIA SE A!=B PARA EVITAR IR E VOLTAR NA MESMA CIDADE
	def geraFitnes(self, mat, pos): 																						#AVALIA CADA ROTA POSSIVEL DA POPULACAO
		try:
			d = []
			e = mat[pos:]
			mat = mat[pos:]
			f = self.cidades
			tenhoTodasCidades = ((self.__sublist(mat, f) and True or False) and 1 or 100)							#VERIFICA SE ROTA SENDO AVALIADA POSSUI TODAS AS CIDADES 
			d.extend(self.distancia[mat[i]][mat[i+1]] for i in range(len(mat)))				
			return [tenhoTodasCidades, sum(d)]																   #SOMA VALOR DE DISTANCIA ENTRE CIDADES DA ROTA 
		except Exception, e:
			return [tenhoTodasCidades, sum(d)]
	def load(self, url):
		try:
			file = open(url, 'r')
			fileLines= file.readlines()
			for linha in fileLines:
				linha = linha.split(" ")
				for indice, distancia in enumerate(linha):
					pass
			#LE CADA LINHA E ATRIBUI VALOR DE DISTANCIAS	
		except Exception, e:
			print e
	def __sublist(self, filho,  mae):
		try:
			contem=[]
			contem.extend((item in filho and 1 or 0) for item in mae)										#VERIFICA SE ROTA POSSUI TODAS CIDADES
			if 0 in contem:
				return False
			else:
				return True
		except Exception, e:
			print 'Erro na busca de sublista, ', e
	def __crossover(self):																									#IMENDA ROTAS MAIS BEM AVALIADAS EM ROTAS MAL AVALIADAS A PARTIR DE PONTO EM COMUM
		try:
			tamCrossOver = round(ceil(self.tamPopulacao / 2)* self.crossover)														#NUMERO DE INDIVIDUOS QUE SOFRERAO MUTACAO
			faixa = int(ceil(tamCrossOver / self.NUM_THREADS))
			r = int((tamCrossOver>self.NUM_THREADS and self.NUM_THREADS or tamCrossOver))                     #VERIFICA SE NUM THREADS E MAIOR QUE NUM ELEMENTOS QUE SOFRERAO MUTACAO
			threads = []
			for i in range(r):
				threads.append(self.__startThreads('self.geraCrossOver', {'ini':i+1, 'tam':faixa}))				#DISPARANDO THREADS PARA EFETUAR MUTACAO NOS PIORES ELEMENTOS DA POPULACAO EM FAIXAS
			self.__endThreads(threads)
		except Exception, e:
			print e
	def geraCrossOver(self, ini, tam, nodo=None):
		try:
			tamC = self.tamPopulacao
			ini = tamC - (tam*ini)
			flag = True
			limite = ini + tam
			numCidades = len(self.cidades)
			melhorRota = self.populacao[0][2:]							#AS CIDADES DA MELHOR ROTA, 2 EM DIANTE POS 0 E 1 SAO AVALIACOES
			while ini < limite:
				if limite>=self.tamPopulacao:
					break
				while nodo == None:
					posCorte = random.randint(3, len(self.cidades)-1)																		#PONTO DE CORTE ONDE SERA FEITO A JUNCAO
					nodo = (lambda nodo: nodo in melhorRota and nodo or None)(self.populacao[ini][posCorte])
				del self.populacao[ini][:2]																												#RETIRA VALORES AVALIACAO
				v = {len(self.populacao[ini][:self.populacao[ini].index(nodo)]):'esq', len(self.populacao[ini][self.populacao[ini].index(nodo):])-1:'dir'}			#NUMERO DE ELEMENTOS A DIREITA E ESQUERD DA POSICAO DE CORTE
				g = {len(melhorRota[:melhorRota.index(nodo)]):'esq', len(melhorRota[melhorRota.index(nodo):])-1:'dir'}			#NUMERO DE ELEMENTOS A DIREITA E ESQUERD DA POSICAO DE CORTE DA MELHOR ROTA
				ladoV = max(v.items())																												#CRUZAR O LADO QUE TIVER MAIOR NUMERO DE ELEMENTOS [0] = LADO [1] = NUM ELEM
				ladoG = max(g.items())																									#CRUZAR O LADO QUE TIVER MAIOR NUMERO DE ELEMENTOS [0] = LADO [1] = NUM ELEM
				cont=0
				c=0
				######################################################	
				#VALIDAR NUM ELEMENTOS EQUIPARANDO AO VETOR BASE ( MELHOR ROTA)
				######################################################	
				if ladoG[0]<ladoV[0]:
					ladoV = min(v.items())																									#MANTER O LADO DO MELHOR VETOR COMO MAIOR PARA NAO FALTAR INDICE
				indiceNodo = self.populacao[ini].index(nodo) 
				indiceNodoG = melhorRota.index(nodo)
				if ladoV[1] == 'esq':
					try:
						if indiceNodo>0:
							del self.populacao[ini][:indiceNodo-1]																	#DELETA ELEMENTOS A ESQUERDA DO INICIO ATE O INDICE DO VETOR DE JUNCAO
						indiceNodo = (indiceNodo > 0 and (indiceNodo - 1))
						for indice in range(indiceNodo):
							indiceNodoG = (ladoG[1] == 'dir' and (indiceNodoG +1) or (indiceNodoG -1))
							self.populacao[ini].insert(indice, melhorRota[indiceNodoG])								#ADICIONANDO ELEMENTOS A DIREITA NO VETOR DE MELHOR ROTA
					except Exception, e:
						pass
				else:
					try:
						indiceNodo = self.populacao[ini].index(nodo) 
						if indiceNodo<len(self.populacao[ini])-1:
							del self.populacao[ini][indiceNodo+1:]																	#DELETA ELEMENTOS A ESQUERDA DO INICIO ATE O INDICE DO VETOR DE JUNCAO
						indices = []
						ind = indiceNodo
						id = len(self.cidades) - indiceNodo
						while len(indices)  < id:
							ind+=1
							indices.append(ind)
						for indice in indices:
							indiceNodoG = (ladoG[1] == 'dir' and (indiceNodoG +1) or (indiceNodoG -1))
							self.populacao[ini].insert(indice, melhorRota[indiceNodoG])								#ADICIONANDO ELEMENTOS A DIREITA NO VETOR DE MELHOR ROTA
					except Exception, e:
						pass
				############################################
				#INSERIR ELEMENTOS PARA QUE ROTA CONTENHA TODAS CIDADES
				############################################
				list = []
				list= self.populacao[ini]
				c = 0
				try:
					while not self.__sublist(self.populacao[ini], self.cidades) and c<50:																				#TENTO 20 VEZES INSERIR ELEMENTO NA LISTA PARA COMPLETA-LA
						cont=0
						c+=1
						elem = self.cidades[random.randint(0, len(self.cidades)-1)]
						while elem in list and cont < 50:
							elem = self.cidades[random.randint(0, len(self.cidades)-1)]
							cont+=1
						if cont < 50:
							if self.adjacencia(elem, self.populacao[ini][len(self.populacao[ini])-1]):																		#VERIFICA ADJACENCIA ENTRE O ELEMENTO E O ULTIMO DO VETOR
								self.populacao[ini].append(elem)
								break
				except Exception, e:
					print 'Erro ao completar rota, ', e
				res = self.geraFitnes(self.populacao[ini], 0)																														#VERIFICO AQUI SE TAMANHO TOTAL DE ELEMENTOS JA FOI CRIADO ANTES SE INSERIR CADA ELEMENTO
				self.populacao[ini].insert(0, res[0])
				self.populacao[ini].insert(1, res[1])
				ini+=1
		except Exception, e:
			pass
	def __header(self):
		try:
			print "**************************************************************************************"
			print "*   ALGORITMO GENETICO  - HEURISTICA DO CAIXEIRO VIAJANTE              UNI-BH        *"
			print "*   AUTOR: CESAR T. SILVA, SABRINE HEQUER - cesarts25@gmail.com / sabrinesa@gmail.com*"
			print "*   DISCIPLINA: INTELIGENCIA ARTIFICIAL       PROF: ANA PAULA LADEIRA  CCM7          *"
			print "**************************************************************************************"
			print ""
			print "                   PARAMETROS DE ENTRADA PARA O AG             "
			print "PROBABILIDADE DE MUTACAO  = %f"%self.mutacao
			print "PROBABILIDADE DE CRUZAMENTO = %f"%self.crossover
			print "PROBABILIDADE DE NAO ALCANCABILIDADE ENTRE CIDADES = 1/%d"%self.NAOALCANCO
			print "TAMANHO DA POPULACAO = %d"%self.tamPopulacao
			print "CIDADES - ",  self.cidades
			print "DISTANCIA MAXIMA ENTRE AS CIDADES = %d"%self.MAX_DIST
			print "NUMERO DE GERACOES = %d"%self.geracoes
			print "NUMERO DE THREADS UTILIZADAS = %d"%self.NUM_THREADS
			print ""
			print "                   MATRIZ DE ADJACENCIA             "
			c = " "
			for i in self.cidades:
				c += "    "+i
			print c
			for i in self.cidades:
				c = []
				for j in self.cidades:
					c.append(self.distancia[i][j])
				print i, c
			print ""
			print ""
			print "                   RESULTADOS OBTIDOS             "
			print "MELHOR ROTA - ", self.populacao[0][2:]
			print "CUSTO EM KM - ", self.populacao[0][1]
			print "TEMPO GASTO PELO ALGORITMO - ", self.time, " segundos."
			print ""
			pop = raw_input("IMPRIMIR POPULACAO (S/N):  ")
			if pop.lower() =='s':
				print "                   POPULACAO  INICIAL           "
				for i , j in enumerate(self.populacaoInicial):
					print i , '-  ', j
			if pop.lower() =='s':
				print "                   POPULACAO  FINAL           "
				for i , j in enumerate(self.populacao):
					print i , '-  ', j
			print ""
			print "                BELO HORIZONTE %s"%(strftime("%d/%m/%Y"))
		except Exception, e:
			print e

###################
#INSTANCIA CLASSE
####################
if __name__ == "__main__":
	try:
		print "           --  COLETA DE DADOS -- "
		ger = input("NUMERO DE GERACOES: ")
		pop = input("TAMANHO DA POPULACAO: ")
		citys = input("NUMERO DE CIDADES: ")
		c = []
		c.extend(str(city) for city in range(citys))
		print "                    CALCULANDO ROTA..."
		ag =  AG(0.3,0.7,pop,'2x+30x2', c, 1200, ger,  4, 50)
	except Exception, e:
		print e
