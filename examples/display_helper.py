from IPython.display import HTML

def clean():
    HTML('''<script>
    document.querySelector('div.jp-RenderedText[data-mime-type='application/vnd.jupyter.stderr']').display = 'none';
    </script>''')
