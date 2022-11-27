from pyModbusTCP.client import ModbusClient
from time import sleep
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
import math


class ClienteMODBUS():
    """
    Classe Cliente MODBUS
    """

    def __init__(self, server_ip, porta, scan_time=1):
        """
        Construtor
        """
        self._cliente = ModbusClient(host=server_ip, port=porta)
        self._scan_time = scan_time

    def atendimento(self):
        """
        Método para atendimento do usuário
        """
        self._cliente.open()
        try:
            atendimento = True
            while atendimento:
                sel = input(
                    "Deseja realizar uma leitura, escrita ou configuração? (1- Leitura | 2- Escrita | 3- Configuração |4- Sair): ")

                if sel == '1':
                    tipo = input(
                        """Qual tipo de dado deseja ler? (1- Holding Register) |2- Coil |3- Input Register |4- Discrete Input| 5- Float | 6- String) :""")
                    addr = input(f"Digite o endereço da tabela MODBUS: ")
                    nvezes = input("Digite o número de vezes que deseja ler: ")
                    for i in range(0, int(nvezes)):
                        print(
                            f"Leitura {i+1}: {self.lerDado(int(tipo), int(addr))}")
                        sleep(self._scan_time)
                elif sel == '2':
                    tipo = input(
                        """Qual tipo de dado deseja escrever? (1- Holding Register) |2- Coil |3- Float | 4- String) :""")
                    addr = input(f"Digite o endereço da tabela MODBUS: ")
                    valor = input(f"Digite o que deseja escrever: ")
                    self.escreveDado(int(tipo), int(addr), valor)

                elif sel == '3':
                    scant = input("Digite o tempo de varredura desejado [s]: ")
                    self._scan_time = float(scant)

                elif sel == '4':
                    self._cliente.close()
                    atendimento = False
                else:
                    print("Seleção inválida")
        except Exception as e:
            print('Erro no atendimento: ', e.args)

    def lerDado(self, tipo, addr):
        """
        Método para leitura de um dado da Tabela MODBUS
        """
        if tipo == 1:
            # (addr -> coluna end onde vai começar a leitura do valor,
            return self._cliente.read_holding_registers(addr, 1)[0]
            # "valor"-> número de registradores que deseja ler, partindo da linha do addr)
            # '[0]' utiizado para fazer o retorno ser um número, porque o return dos métdos de leitura são listas

        if tipo == 2:
            return self._cliente.read_coils(addr, 1)[0]

        if tipo == 3:
            return self._cliente.read_input_registers(addr, 1)[0]

        if tipo == 4:
            return self._cliente.read_discrete_inputs(addr, 1)[0]

        if tipo == 5:
            # faz a leitura dos registradores a partir do endereço passado e do numero de registradores passados
            result = self._cliente.read_holding_registers(addr, 2)
            decoder = BinaryPayloadDecoder.fromRegisters(
                result)  # decodifica em um payload
            # retorna o valor do float a partir do valor do decoder obitido
            return decoder.decode_32bit_float()

        if tipo == 6:
            # lê primeiro valor do primeiro registrador que é o tamanho da string
            tam = self._cliente.read_holding_registers(addr, 1)[0]
            # Lê os resgistradores a frente até o tamanho/2, pois o registrador armazena 2 char em cada
            result = self._cliente.read_holding_registers(
                addr+1, math.ceil(tam/2))
            decoder = BinaryPayloadDecoder.fromRegisters(
                result)  # decodifica em um payload
            # decodifica o payload em string
            decoder = decoder.decode_string(tam).decode()
            return decoder

    def escreveDado(self, tipo, addr, valor):
        """
        Método para a escrita de dados na Tabela MODBUS
        """
        if tipo == 1:
            return self._cliente.write_single_register(addr, valor)

        if tipo == 2:
            return self._cliente.write_single_coil(addr, valor)

        if tipo == 3:
            builder = BinaryPayloadBuilder()  # cria um objeto BinaryPayloadBuilder
            # Adciona o valor em formato float no builder
            builder.add_32bit_float(float(valor))
            # converte o buffer do payload em um de registro que pode ser usado como um bloco de contexto
            payload = builder.to_registers()
            # escreve no endereço passado o payload em questão
            return self._cliente.write_multiple_registers(addr, payload)

        if tipo == 4:
            builder = BinaryPayloadBuilder()  # cria um objeto BinaryPayloadBuilder
            v = len(valor)  # obtem o número de dígitos da string
            # escreve no primeiro registrador no endereço passado o numero de dígitos da string
            self._cliente.write_single_register(addr, v)
            # adiciona o valor em forma de stirng no builder
            builder.add_string(str(valor))
            # converte o buffer, em formato de lita, do payload em um de registro que pode ser usado como um bloco de contexto
            payload = builder.to_registers()
            # escreve no endereço a frente o payload, que é a informação que deve ser armazenada depois da conversão
            return self._cliente.write_multiple_registers(addr+1, payload)
