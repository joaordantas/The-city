function construirEscola() {

    const custo = 2000;

    if (cidade.dinheiro >= custo) {

        cidade.dinheiro -= custo;
        cidade.educacao += 5;

        console.log("Escola construída!");
        console.log("Dinheiro:", cidade.dinheiro);
        console.log("Educação:", cidade.educacao);

    } else {

        console.log("Dinheiro insuficiente!");

    }
}