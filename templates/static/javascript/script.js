var menu_lateral = document.querySelector('.fixed-side-bar') // quero pegar esse item para testar se ele tem ou nao a coisa
var box_principal = document.querySelector('.box')



$('.btn-abre-menu-lateral').click(function () {
    $('.fixed-side-bar').toggleClass('mostrar')
    $('.box').toggleClass('expandir')
    localStorage.setItem('aberto', 'true')
    console.log('oi')
})

$('.btn-fecha-menu-lateral').click(function () {
    $('.fixed-side-bar').toggleClass('mostrar')
    $('.box').toggleClass('expandir')
    localStorage.setItem('aberto', 'false')

})


window.onload = function () {
    console.log(localStorage.getItem('aberto'))
    if (localStorage.getItem('aberto') == 'false') {
        console.log('oi', menu_lateral.classList.contains('mostrar'))
        menu_lateral.classList.add('mostrar')
        box_principal.classList.add('expandir')
    }
}

/*******/


/**/
$('.btn-show').click(function () {
    $('.nav-bar-aula-modulo').toggleClass('show')
    $('.nav-bar-aula-aulas').toggleClass('show')
    $('.nome-professor').toggleClass('show')
    $('.titulo-modulo').toggleClass('show')
    $('.nav-bar-aula-modulo span').toggleClass('move')
})

$('.label-ingles').click(function () {
    $('.box-modulos-ingles').toggleClass('show')
    $('.btn-show-ingles').toggleClass('move')
})
$('.label-alemao').click(function () {
    $('.box-modulos-alemao').toggleClass('show')
    $('.btn-show-alemao').toggleClass('move')

})
$('.label-noruegues').click(function () {
    $('.box-modulos-noruegues').toggleClass('show')
    $('.btn-show-noruegues').toggleClass('move')

})


$('.abre-usuario').click(function () {
    $('ul.drop-menu-usuario li').toggleClass('abre')
    $('ul.drop-menu-usuario').toggleClass('abre')
})

$('.abre-cadastro').click(function () {
    $('ul.drop-menu-cadastro li').toggleClass('abre')
    $('ul.drop-menu-cadastro').toggleClass('abre')
})

