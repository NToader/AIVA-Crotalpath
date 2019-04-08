function display_tiff(file, fileList, rects, prediction) {
    var reader = new FileReader();
    reader.onload = function (e) {
        Tiff.initialize({
            TOTAL_MEMORY: 10000000
        });
        var tiff = new Tiff({
            buffer: e.target.result,
            width: 100,
            height: 100
        });
        var canvas = tiff.toCanvas();

        rects.forEach(function (rect) {
            paint_rect(canvas, rect);
        });

        var domObj = $('<div class="card d-flex flex-column text-white bg-dark m-3"></div>');
        $(domObj)[0].append($('<div class="card-header text-center">' + file.name + '</div>')[0]);
        $(domObj)[0].append(canvas);
        $(domObj)[0].append($('<div class="card-footer text-center"><h5>' + prediction + '</h5></div>')[0]);
        fileList.append(domObj);
    };
    reader.readAsArrayBuffer(file);
}

function display_image(file, fileList, rects, prediction) {
    var reader = new FileReader();
    reader.onload = function (e) {
        var canvas = $('<canvas></canvas>')[0];
        var ctx = canvas.getContext("2d");

        var image = new Image();
        image.onload = function () {
            canvas.width = image.width;
            canvas.height = image.height;
            ctx.drawImage(image, 0, 0);
            rects.forEach(function (rect) {
                paint_rect(canvas, rect);
            });

            var domObj = $('<div class="card d-flex flex-column text-white bg-dark m-3"></div>');
            $(domObj)[0].append($('<div class="card-header text-center">' + file.name + '</div>')[0]);
            $(domObj)[0].append(canvas);
            $(domObj)[0].append($('<div class="card-footer text-center"><h5>' + prediction + '</h5></div>')[0]);
            fileList.append(domObj);
        };
        image.src = e.target.result;


    };
    reader.readAsDataURL(file);
}

function paint_rect(canvas, rect) {
    var ctx = canvas.getContext("2d");
    let x = rect[0];
    let y = rect[1];
    let x2 = rect[2];
    let y2 = rect[3];
    ctx.beginPath();
    ctx.lineWidth = "5";
    ctx.strokeStyle = "#1c7fff";
    ctx.rect(x, y, x2, y2);
    ctx.stroke();
}

$(document).ready(function () {
    $('#upload_input').on('change', function () {
        var fileList = $('#file_list');
        fileList.empty();
        fileList.append($(' <div class="fa-3x">' +
            ' <i class="fas fa-circle-notch fa-spin text-dark"></i>' +
            '</div>'));
        $('#side-bar').css('width', '500px');

        var files = $(this)[0].files;
        $.ajax({
            url: 'tasks',
            type: 'post',
            cache: false,
            data: new FormData($('#upload_form')[0]),
            processData: false,
            contentType: false,
            success: function (data, textStatus, request) {
                var repeat = setInterval(function () {
                    $.ajax({
                        url: request.getResponseHeader('location'),
                        type: 'get',
                        cache: false,
                        processData: false,
                        contentType: false,
                        success: function (data, textStatus, request) {
                            if (request.responseJSON.length !== undefined) {
                                var dataList = request.responseJSON;
                                clearInterval(repeat);
                                $('#file_container').css('display', 'flex');
                                fileList.empty();

                                var dataObj = {};
                                dataList.forEach(function (data) {
                                    var id = data.identifier.split('/').pop();
                                    dataObj[id] = data;
                                });

                                for (var i = 0; i < files.length; i++) {
                                    var file = files[i];
                                    var crotal = dataObj[file.name];
                                    var extension = file.name.split('.').pop().toLowerCase();
                                    if (extension === 'tif' || extension === 'tiff')
                                        display_tiff(file, fileList, crotal.bounding_rects, crotal.digits);
                                    else
                                        display_image(file, fileList, crotal.bounding_rects, crotal.digits);
                                }

                            }
                        }
                    });
                }, 1000);
            }
        });

    });
});

function upload() {
    $('#upload_input').click()
}