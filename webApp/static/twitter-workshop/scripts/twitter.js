function getCookie(c_name)
{
    if (document.cookie.length > 0)
    {
        c_start = document.cookie.indexOf(c_name + "=");
        if (c_start != -1)
        {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
            if (c_end == -1) c_end = document.cookie.length;
            return unescape(document.cookie.substring(c_start,c_end));
        }
    }
    return "";
 }

function get_user_profile_picture(id) {
    console.log(Date.now());
    $.ajax({
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        type: "POST",
        url: '/get_user_profile_picture',
        async: false,
        data: {
            id: id
        },
        success: function (response) {

        },
        complete: function (response) {
            profile_picture_url =  response.responseJSON;
        }
    });
console.log(Date.now());
    return profile_picture_url;
}