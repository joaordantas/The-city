print("== JOGO DE XADREZ E DAMAS ==")

print("=============================")

print("Escolha o modo de jogo:")
print("1 - PvP (Jogador vs Jogador)")
print("2 - PvE (Jogador vs Computador)")

modo_de_jogo = input("Digite sua escolha: ")

print("=============================")

if modo_de_jogo == "1":

    print("Qual o nome dos jogadores?")

    jogador1 = input("Jogador 1: ")
    jogador2 = input("Jogador 2: ")

    print(f"Bem-vindos, {jogador1} e {jogador2}! Vamos começar o jogo.")

elif modo_de_jogo == "2":

    print("Qual o nome do jogador?")

    jogador1 = input("Jogador: ")
    jogador2 = "Computador"

    print(f"Bem-vindo, {jogador1}! Vamos começar o jogo.")

else:
    print("Opção inválida. Por favor, reinicie o jogo e escolha uma opção válida.")