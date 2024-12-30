$(document).ready(function() {
    // Inicialização da tabela de dados na aba "Carteira"
    var table = $('#tabela').DataTable({
        "pageLength": 50,
        "scrollX": true, // Ativar a rolagem horizontal
        dom: 'Bfrtip',
        buttons: [
            {
                extend: 'excelHtml5',
                text: 'Exportar para Excel',
                exportOptions: {
                    columns: ':visible',
                    modifier: {
                        page: 'all'
                    },
                    format: {
                        header: function (data, columnIdx) {
                            return $('#tabela thead tr:first-child th').eq(columnIdx).text();
                        }
                    }
                }
            }
        ],
        columnDefs: [
            { "width": "200px", "targets": 0 },  // Coluna 0 (Cliente)
            { "width": "150px", "targets": 1 },  // Coluna 1 (Tipo Orçamento)
            { "width": "150px", "targets": 2 },  // Coluna 2 (Peça)
            { "width": "150px", "targets": 3 },  // Coluna 3 (Rastreabilidade)
            { "width": "100px", "targets": 4 },  // Coluna 4 (Quantidade)
            { "width": "150px", "targets": 5 },  // Coluna 5 (Data Recebimento)
            { "width": "150px", "targets": 6 },  // Coluna 6 (Data Inicio OS)
            { "width": "150px", "targets": 7 },  // Coluna 7 (Data Fim OS)
            { "width": "150px", "targets": 8 },  // Coluna 8 (Valor Bruto)
            { "width": "150px", "targets": 9 },  // Coluna 9 (Valor Líquido)
            { "width": "200px", "targets": 10 }, // Coluna 10 (Responsável Comercial)
            { "width": "150px", "targets": 11 }, // Coluna 11 (Status OS)
            { "width": "150px", "targets": 12 }, // Coluna 12 (Número NF)
            { "width": "150px", "targets": 13 }, // Coluna 13 (Código OS)
            { "width": "150px", "targets": 14 }, // Coluna 14 (Orçamento)
            { "width": "150px", "targets": 15 }, // Coluna 15 (Data Orçamento)
            { "width": "200px", "targets": 16 }, // Coluna 16 (Representante)
            { "width": "150px", "targets": 17 }  // Coluna 17 (OC Cliente)
        ],
        initComplete: function () {
            this.api().columns().every(function () {
                var column = this;
                $('input', column.header()).on('keyup change', function () {
                    if (column.search() !== this.value) {
                        column
                            .search(this.value)
                            .draw();
                    }
                });
            });
        }
    });

    // Função para formatar valores monetários
    function formatMoney(value) {
        if (!value || value === 0 || value === "0E-8") {
            return "R$ 0,00";
        }
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL',
            minimumFractionDigits: 2
        }).format(value);
    }

    // Função para formatar datas
    function formatDate(value) {
        let date = new Date(value);
        if (isNaN(date.getTime())) {
            return value ? value : ''; // Se a data for inválida ou `None`, retorna em branco
        }
        return date.toLocaleDateString('pt-BR');
    }

    // Função para aplicar a formatação nas células da tabela
    function applyTableFormatting() {
        table.rows({ filter: 'applied' }).every(function() {
            var data = this.data();
            var valorBruto = parseFloat(data[8]) || 0;
            var valorLiquido = parseFloat(data[9]) || 0;

            $(this.node()).find('td').eq(8).html(valorBruto !== 0 ? formatMoney(valorBruto) : ''); // "Valor Bruto"
            $(this.node()).find('td').eq(9).html(valorLiquido !== 0 ? formatMoney(valorLiquido) : ''); // "Valor Líquido"

            $(this.node()).find('td').eq(5).html(data[5] ? formatDate(data[5]) : ''); // Data Recebimento
            $(this.node()).find('td').eq(6).html(data[6] ? formatDate(data[6]) : ''); // Data Inicio OS
            $(this.node()).find('td').eq(7).html(data[7] ? formatDate(data[7]) : ''); // Data Fim OS
            $(this.node()).find('td').eq(15).html(data[15] ? formatDate(data[15]) : ''); // Data Orçamento

            for (let i = 0; i < data.length; i++) {
                if (!data[i] || data[i] === 'None') {
                    $(this.node()).find('td').eq(i).html('');
                }
            }
        });
    }

    // Chamar a função de formatação sempre que a tabela for desenhada
    table.on('draw', function() {
        applyTableFormatting();
        calculateTotals();
    });

    // Função para calcular e atualizar os valores dos cards
    function calculateTotals() {
        var totalBruto = 0;
        var totalLiquido = 0;

        table.rows({ filter: 'applied' }).every(function() {
            var data = this.data();
            var valorBruto = parseFloat(data[8].replace(/[^\d,.-]/g, '').replace(',', '.')) || 0;
            var valorLiquido = parseFloat(data[9].replace(/[^\d,.-]/g, '').replace(',', '.')) || 0;

            totalBruto += valorBruto;
            totalLiquido += valorLiquido;
        });

        $('#totalValorBruto').text(formatMoney(totalBruto));
        $('#totalValorLiquido').text(formatMoney(totalLiquido));
    }

    applyTableFormatting();
    calculateTotals();

    // Função para a aba de "Responsáveis"
    function filtrarDados(dados, cliente, situacoes) {
		return dados.filter(function (row) {
			var clienteMatch = !cliente || row[0].toLowerCase().includes(cliente.toLowerCase());

			// Verificar se uma das situações selecionadas corresponde à coluna de situação (coluna 18)
			var situacaoMatch = !situacoes.length || situacoes.includes(row[18]);

			return clienteMatch && situacaoMatch;
		});
	}

    function atualizarGraficoResponsavelComercial(dados) {
		var somaPorResponsavel = {};
		var totalPecas = 0;

		dados.forEach(function (row) {
			var responsavel = row[10]; // Coluna 11: Responsável Comercial
			var valorLiquido = parseFloat(row[9]) || 0; // Coluna 10: Valor Líquido
			var quantidadePecas = parseInt(row[4]) || 0; // Coluna 5: Quantidade

			if (!somaPorResponsavel[responsavel]) {
				somaPorResponsavel[responsavel] = { valorLiquido: 0, pecas: 0 };
			}
			somaPorResponsavel[responsavel].valorLiquido += valorLiquido;
			somaPorResponsavel[responsavel].pecas += quantidadePecas;
			totalPecas += quantidadePecas;
		});

		var labels = Object.keys(somaPorResponsavel);
		var valoresLiquidos = labels.map(function (responsavel) {
			return somaPorResponsavel[responsavel].valorLiquido;
		});
		var pecasPorResponsavel = labels.map(function (responsavel) {
			return somaPorResponsavel[responsavel].pecas;
		});

		// Atualiza o valor total de peças (removido do gráfico e do rodapé)
		$('#totalPecas').text(totalPecas);

		// Destruir o gráfico anterior se ele existir
		if (window.graficoResponsavelComercial && typeof window.graficoResponsavelComercial.destroy === 'function') {
			window.graficoResponsavelComercial.destroy();
		}

		// Criar o gráfico
		var ctx = $('#graficoResponsavelComercial');
		window.graficoResponsavelComercial = new Chart(ctx, {
			type: 'bar', // Mantendo como barra horizontal
			data: {
				labels: labels,
				datasets: [{
					label: 'Valor Líquido (R$)',
					data: valoresLiquidos,
					backgroundColor: 'rgba(0, 123, 255, 0.7)', // Azul forte para o fundo da barra
					borderColor: 'rgba(0, 123, 255, 1)', // Azul forte para a borda
					borderWidth: 1
				}]
			},
			options: {
				indexAxis: 'y', // Gráfico de barras horizontais
				scales: {
					x: {
						beginAtZero: true,
						ticks: {
							callback: function (value) {
								return 'R$ ' + value.toLocaleString('pt-BR', { minimumFractionDigits: 2 });
							}
						}
					}
				},
				plugins: {
					tooltip: {
						callbacks: {
							label: function (context) {
								var valorLiquido = context.raw.toLocaleString('pt-BR', { minimumFractionDigits: 2 });
								var pecas = pecasPorResponsavel[context.dataIndex];
								return `R$ ${valorLiquido} | Peças: ${pecas}`;
							}
						}
					},
					legend: {
						display: false // Remover legenda se necessário
					}
				},
				elements: {
					bar: {
						borderWidth: 2,
					}
				},
				layout: {
					padding: {
						top: 0,
						bottom: 0,
						left: 0,
						right: 0
					}
				}
			}
		});
	}
	
	function atualizarGraficoClientes(dados) {
		var somaPorCliente = {};
		var totalPecas = 0;

		dados.forEach(function (row) {
			var cliente = row[0]; // Coluna 1: Cliente
			var valorLiquido = parseFloat(row[9]) || 0; // Coluna 10: Valor Líquido
			var quantidadePecas = parseInt(row[4]) || 0; // Coluna 5: Quantidade

			if (!somaPorCliente[cliente]) {
				somaPorCliente[cliente] = { valorLiquido: 0, pecas: 0 };
			}
			somaPorCliente[cliente].valorLiquido += valorLiquido;
			somaPorCliente[cliente].pecas += quantidadePecas;
			totalPecas += quantidadePecas;
		});

		// Ordenar os clientes pelo valor líquido de forma decrescente
		var sortedClientes = Object.keys(somaPorCliente).sort(function(a, b) {
			return somaPorCliente[b].valorLiquido - somaPorCliente[a].valorLiquido;
		});

		var labels = sortedClientes;
		var valoresLiquidos = labels.map(function (cliente) {
			return somaPorCliente[cliente].valorLiquido;
		});
		var pecasPorCliente = labels.map(function (cliente) {
			return somaPorCliente[cliente].pecas;
		});

		// Destruir o gráfico anterior se ele existir
		if (window.graficoClientes && typeof window.graficoClientes.destroy === 'function') {
			window.graficoClientes.destroy();
		}

		// Criar o gráfico
		var ctx = $('#graficoClientes');
		window.graficoClientes = new Chart(ctx, {
			type: 'bar', // Gráfico de barras horizontais
			data: {
				labels: labels,
				datasets: [{
					label: 'Valor Líquido (R$)',
					data: valoresLiquidos,
					backgroundColor: 'rgba(0, 123, 255, 0.7)', // Azul forte para o fundo da barra
					borderColor: 'rgba(0, 123, 255, 1)', // Azul forte para a borda
					borderWidth: 1
				}]
			},
			options: {
				indexAxis: 'y', // Configuração para barras horizontais
				responsive: true,
				maintainAspectRatio: false, // Permitir ajuste dinâmico
				scales: {
					x: {
						beginAtZero: true,
						ticks: {
							callback: function (value) {
								return 'R$ ' + value.toLocaleString('pt-BR', { minimumFractionDigits: 2 });
							}
						},
						grid: {
							display: false // Remove o fundo das linhas de grade do gráfico
						}
					},
					y: {
						grid: {
							display: false // Remove o fundo das linhas de grade do gráfico
						}
					}
				},
				plugins: {
					tooltip: {
						callbacks: {
							label: function (context) {
								var valorLiquido = context.raw.toLocaleString('pt-BR', { minimumFractionDigits: 2 });
								var pecas = pecasPorCliente[context.dataIndex];
								return `R$ ${valorLiquido} | Peças: ${pecas}`;
							}
						}
					},
					legend: {
						display: false // Remover legenda se necessário
					}
				},
				layout: {
					padding: {
						top: 0,
						bottom: 0,
						left: 0,
						right: 0
					}
				}
			}
		});
	}

    function atualizarResponsaveis() {
		var cliente = $('#filtro-cliente').val();

		// Obter as situações selecionadas
		var situacoes = $('#filtro-situacao').val() || [];

		var dadosFiltrados = filtrarDados(dados, cliente, situacoes);
		
		// Atualizar o gráfico de Responsáveis
		atualizarGraficoResponsavelComercial(dadosFiltrados);

		// Atualizar o gráfico de Clientes
		atualizarGraficoClientes(dadosFiltrados); // Novo gráfico de Clientes

		atualizarGraficoResponsavelComercial(dadosFiltrados);
	}

    $('#filtro-cliente, #filtro-situacao').on('keyup change', function () {
        atualizarResponsaveis();
    });

    atualizarResponsaveis();
});
