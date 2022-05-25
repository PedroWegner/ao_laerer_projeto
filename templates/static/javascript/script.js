$('.btn-show').click(function () {
    $('.nav-bar-aula-modulo').toggleClass('show')
    $('.nav-bar-aula-aulas').toggleClass('show')
    $('.nome-professor').toggleClass('show')
    $('.titulo-modulo').toggleClass('show')
    $('.nav-bar-aula-modulo span').toggleClass('move')
})


$('.label-normais').click(function () {
    $('.meu-ensino-normais').toggleClass('show')
})

$('.label-licenciadas').click(function () {
    $('.meu-ensino-licenciadas').toggleClass('show')
})

$('.label-questoes').click(function () {
    $('.meu-ensino-questoes').toggleClass('show')
})

$('.abre-usuario').click(function () {
    $('ul.drop-menu-usuario li').toggleClass('abre')
    $('ul.drop-menu-usuario').toggleClass('abre')
})

$('.abre-cadastro').click(function () {
    $('ul.drop-menu-cadastro li').toggleClass('abre')
    $('ul.drop-menu-cadastro').toggleClass('abre')
})

{
    $('.muda-tema').click(function () {
        $(':root').toggleClass('light')
        if (localStorage.getItem('claro') == 'false') {
            localStorage.setItem('claro', 'true')
        }
        else {
            localStorage.setItem('claro', 'false')
        }

    })

    window.onload = function () {
        if (localStorage.getItem('claro') == 'true') {
            document.querySelector(':root').classList.add('light')
        }
        else {
            document.querySelector(':root').classList.remove('light')
        }
    }
}

