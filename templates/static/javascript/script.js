$('.btn-show').click(function () {
    $('.side-nav-bar').toggleClass('show')
    $('.side-nav-bar-items').toggleClass('show')
    $('.sive-bar-item').toggleClass('show')
    $('.sive-bar-item').toggleClass('show')
    $('.sive-bar-item').toggleClass('show')
    $('.side-nav-bar span').toggleClass('move')
})


$('.label-normais').click(function () {
    $('.meu-ensino-normais').toggleClass('show')
    $('.label-normais span').toggleClass('move')
})

$('.label-licenciadas').click(function () {
    $('.meu-ensino-licenciadas').toggleClass('show')
    $('.label-licenciadas span').toggleClass('move')
})

$('.label-questoes').click(function () {
    $('.meu-ensino-questoes').toggleClass('show')
    $('.label-questoes span').toggleClass('move')
})
{
    $('.abre-usuario').click(function () {
        $('ul.drop-menu-usuario li').toggleClass('abre')
        $('ul.drop-menu-usuario').toggleClass('abre')
    })

    $('.abre-cadastro').click(function () {
        $('ul.drop-menu-cadastro li').toggleClass('abre')
        $('ul.drop-menu-cadastro').toggleClass('abre')
    })
}
{
    $('.fecha-aviso').click(function () {
        $('#aviso').remove()
    })
}

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