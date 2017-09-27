var showToast = function (type, message, title, timeout, tapToDismiss) {
    if (type === 'error'){
        title = 'Atenção!';
        timeout = 0;
        tapToDismiss = false
    }
    toastr.options = {
        "closeButton": true,
        "debug": false,
        "newestOnTop": true,
        "progressBar": false,
        "positionClass": "toast-top-right",
        "preventDuplicates": false,
        "onclick": null,
        "showDuration": "1",
        "hideDuration": "1",
        "timeOut": timeout,
        "extendedTimeOut": timeout,
        "showEasing": "swing",
        "hideEasing": "linear",
        "showMethod": "fadeIn",
        "hideMethod": "fadeOut",
        "tapToDismiss": tapToDismiss
    };
    toastr[type](message, title)
};