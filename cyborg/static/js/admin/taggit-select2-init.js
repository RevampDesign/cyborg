// In a static/js/taggit_select2_init.js file

$(document).ready(function() {
    $('.taggit-select2').each(function() {
        const url = "/newsletters/tag-lookup/";
        $(this).select2({
            tags: true, // Allows new tags to be entered
            tokenSeparators: [',', ' '], // Separates tags by commas or spaces
            ajax: {
                url: url,
                dataType: 'json',
                delay: 250,
                data: function(params) {
                    return {
                        q: params.term // search term
                    };
                },
                processResults: function(data) {
                    return {
                        results: $.map(data, function(tag) {
                            return {
                                id: tag,
                                text: tag
                            };
                        })
                    };
                },
                cache: true
            }
        });
    });
});