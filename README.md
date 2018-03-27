Horários CNPEM

Software não oficial para controle de horários de entrada e saída no CNPEM. Este software salva os horários de entrada e saída, permitindo carregar e editar cada dia do mês, além de ter uma ferramenta para visualizar estes dados de maneira muito semelhante à folha de ponto, calculando as horas positivas ou horas negativas, se houver. 

Este software segue o mesmo cálculo do cnpem: tolerância de mais ou menos 10 minutos, e inclui 10 minutos de compensação de pontes e feriados.

Descrição de uso:

Aba Editar - permite editar os horários de entrada e saída, basta selecionar a data desejada. As horas devem sempre estar no formato hh:mm. O botão "Hoje" muda a data para a data atual, o botão "Calcular" permite ver hora extra e ausência antes de salvar os dados, o botão "Salvar" calcula e grava os dados do dia e o botão "Limpar" grava todos os campos. Se você almoçar no CNPEM, é preciso habilitar a checkbox "Almoço no CNPEM". Você pode deixar o almoço checado por default, basta descomentar a linha 39 e comentar a linha 96.

Faltas: As faltas devem ser salvas no banco de dados para a contagem correta do extrato de horas, pode-se fazer isso escrevendo "00:00" nos campos Entrada1 e Saida1, ou digitando "Falta" no comentário, porém no meu caso eu prefiro detalhar melhor o motivo da falta no comentário, dando preferência à primeira alternativa portanto.

Férias: Basta digitar "Férias" no comentário dos dias em questão para que ele não desconte nem some horas durante esse período. Também é possível simplesmente não adicionar entradas para esses dias, mas acho melhor deixar todas as informações salvas.

Sábado: O software já reconhece quando a data é um sábado e considera como banco de horas.

Aba Visualizar - Selecione o intervalo de datas desejado e clique em "Carregar" para exibir os dados e o extrato de horas no intervalo. Observe que só é criada uma data quando você clica em "Salvar", portanto se você faltar e não salvar a falta, não será levado em consideração no relatório que você deve 8 horas naquele dia.


Observações: Escrevi este software pois recentemente comecei a almoçar em casa e saio depois das 13h, então o sistema acredita que almoçei no CNPEM e desconta 1h além dos período em que fiquei almoçando. Isso bagunçou toda minha folha de ponto, então achei necessário criar uma ferramenta para facilitar meu controle. Achei que poderia ser útil para outros colegas, então resolvi compartilhar, mas lembrem-se que eu desenvolvi em Linux, então pode ser que a interface fique bagunçada (mais ainda) no Windows.

Sintam-se livres para dar sugestões e/ou editar o código, mas por favor compartilhem se acreditarem que as alterações podem beneficiar outros colegas!
