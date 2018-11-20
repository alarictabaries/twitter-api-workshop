$( document ).ready(function() {

    /* Filter processed tweets table */
    $( "#processed-tw-search" ).keyup(function() {
        $(".list tr").each(function() {
            var $tds_processed = $(this).find('td.processed');
            var $tds_alias = $(this).find('td.alias');
            var $tds_score = $(this).find('td.score');
            if(($tds_processed.length != 0) && ($tds_alias.length != 0) && ($tds_score.length != 0)){
                var $currText_processed = $tds_processed.eq(0).text();
                var $currText_alias = $tds_alias.eq(0).text();
                var $currText_score = $tds_score.eq(0).text();
                if( $( "#processed-tw-search" ).val().startsWith('d>') || $( "#processed-tw-search" ).val().startsWith('d<')) {

                }
                else if( $( "#processed-tw-search" ).val().startsWith('s>') || $( "#processed-tw-search" ).val().startsWith('s<')) {
                    if(($( "#processed-tw-search" ).val().split('>')[1]) || ($( "#processed-tw-search" ).val().split('<')[1])) {
                        if($( "#processed-tw-search" ).val().charAt(1) == ">") {
                            if(parseFloat($tds_score.eq(0).text()) > $( "#processed-tw-search" ).val().split('>')[1]) {
                                $tds_processed[0].closest("tr").style.display = 'table-row';
                            } else {
                                $tds_processed[0].closest("tr").style.display = 'none';
                            }
                        } else if($( "#processed-tw-search" ).val().charAt(1) == "<") {
                            if(parseFloat($tds_score.eq(0).text()) < $( "#processed-tw-search" ).val().split('<')[1]) {
                                $tds_processed[0].closest("tr").style.display = 'table-row';
                            } else {
                                $tds_processed[0].closest("tr").style.display = 'none';
                            }
                        }
                    }
                } else if( ($currText_processed.indexOf($( "#processed-tw-search" ).val()) >= 0) || ($currText_alias.indexOf($( "#processed-tw-search" ).val()) >= 0) || ($currText_score.indexOf($( "#processed-tw-search" ).val()) >= 0)) {
                    $tds_processed[0].closest("tr").style.display = 'table-row';
                } else {
                    $tds_processed[0].closest("tr").style.display = 'none';
                }

            }
        });
    });

    /* Filter basic tweets table */
    $( "#tw-search" ).keyup(function() {
        $(".list tr").each(function() {
            var $tds_text = $(this).find('td.text');
            var $tds_alias = $(this).find('td.alias');
            var $tds_date = $(this).find('td.date');
            if(($tds_text.length != 0) && ($tds_alias.length != 0) && ($tds_date.length != 0)){
                var $currText_text = $tds_text.eq(0).text();
                var $currText_alias = $tds_alias.eq(0).text();
                var $currText_date = $tds_date.eq(0).text();
                if( ($currText_text.indexOf($( "#tw-search" ).val()) >= 0) || ($currText_alias.indexOf($( "#tw-search" ).val()) >= 0) || ($currText_date.indexOf($( "#tw-search" ).val()) >= 0)) {
                    $tds_text[0].closest("tr").style.display = 'table-row';
                } else {
                    $tds_text[0].closest("tr").style.display = 'none';
                }

            }
        });
    });
});
