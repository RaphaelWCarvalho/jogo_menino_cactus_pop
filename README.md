# Menino Cactus — O Palácio das Sombras

Adaptação visual de Prince of Persia com o personagem Menino Cactus, baseada no SDLPoP 1.23. Inclui uniforme verde e amarelo, artes de abertura, ícones e narrativa em português.

## Jogar no Windows

Baixe este repositório pelo botão **Code > Download ZIP** e extraia os arquivos. Abra a pasta `Menino_Cactus_Jogavel` e execute `JOGAR.cmd` ou `Jogo Menino Cactus.exe`.

Outra opção é extrair o pacote `Menino_Cactus_Jogavel.zip`, disponível na raiz. Mantenha os executáveis junto das DLLs e das pastas de dados.

Na apresentação, pressione qualquer tecla para começar. Use as setas para mover, pular e agachar; Shift para passos cuidadosos, agarrar bordas e atacar; Esc para pausar. F6 salva rapidamente e F9 carrega. Os controles completos estão em `Menino_Cactus_Jogavel/COMO JOGAR.txt`.

## Conteúdo do projeto

- `Menino_Cactus_Jogavel/`: jogo portátil, dados, mod, documentação, licenças e código-fonte do motor.
- `arte_mc/`: artes e ícones do personagem.
- Scripts Python na raiz: preparação do mod, personalização da história e dos executáveis e verificações.
- `preview/`: materiais de prévia e distribuição original usada como base pelos scripts.
- `verificacao/`: imagens, replays e relatórios de verificação existentes.
- `versoes/`: pacotes anteriores e cópias de referência.

Os scripts usam Python e Pillow; alguns dependem do Windows e de suas fontes. A criação de vídeo em `preview/build_preview.py` depende também do FFmpeg. As ferramentas baixadas em `preview/tools/`, caches, logs e atalhos locais ficam fora do versionamento.

## Créditos e licença

Motor [SDLPoP](https://github.com/NagyD/SDLPoP), por Dávid Nagy e colaboradores, distribuído sob GPL v3 ou posterior. A licença está em `Menino_Cactus_Jogavel/COPYING`, o código correspondente em `Menino_Cactus_Jogavel/src/` e a documentação original em `Menino_Cactus_Jogavel/README.md`. Consulte também os avisos das bibliotecas de terceiros.

O projeto personaliza a aparência e a apresentação; as fases, controles e mecânicas permanecem os do SDLPoP. As referências do personagem foram fornecidas pelo usuário; as cenas animadas da história são as originais de Prince of Persia. Os avisos de licença do motor não atribuem uma nova licença às artes ou aos demais materiais de terceiros.
