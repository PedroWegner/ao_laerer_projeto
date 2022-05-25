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

$('.muda-tema').click(function () {
    if (localStorage.getItem('claro') == 'false') {
        document.documentElement.style.setProperty('--color-back', '#8B8B8C');
        document.documentElement.style.setProperty('--color-low', '#fff');
        document.documentElement.style.setProperty('--color-medium', '#c2c2c2');
        document.documentElement.style.setProperty('--color-high', '#dcdcdc');
        document.documentElement.style.setProperty('--font-color', '#232424');
        localStorage.setItem('claro', 'true')
    }
    else {
        document.documentElement.style.setProperty('--color-back', '#262626');
        document.documentElement.style.setProperty('--color-low', '#373a3c');
        document.documentElement.style.setProperty('--color-medium', '#222222');
        document.documentElement.style.setProperty('--color-high', '#333');
        document.documentElement.style.setProperty('--font-color', '#E8EBEC');
        localStorage.setItem('claro', 'false')
    }

})
window.onload = function () {
    if (localStorage.getItem('claro') == 'true') {
        document.documentElement.style.setProperty('--color-back', '#8B8B8C');
        document.documentElement.style.setProperty('--color-low', '#fff');
        document.documentElement.style.setProperty('--color-medium', '#c2c2c2');
        document.documentElement.style.setProperty('--color-high', '#dcdcdc');
        document.documentElement.style.setProperty('--font-color', '#232424');

    }
    else {
        document.documentElement.style.setProperty('--color-back', '#262626');
        document.documentElement.style.setProperty('--color-low', '#373a3c');
        document.documentElement.style.setProperty('--color-medium', '#222222');
        document.documentElement.style.setProperty('--color-high', '#333');
        document.documentElement.style.setProperty('--font-color', '#E8EBEC');

    }
}
