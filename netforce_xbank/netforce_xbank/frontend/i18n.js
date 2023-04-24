var translation={
    en: require("./translations/en.js"),
    jp: require("./translations/jp.js"),
}

module.exports.translate=function(k) {
    var lang=localStorage.lang||"en";
    var r=translation[lang][k];
    if (!r) return k;
    return r;
}

module.exports.get_current_lang=function() {
    var lang=localStorage.lang||"en";
    return lang;
}

module.exports.select_lang=function(lang) {
    console.log("i18n.select_lang",lang);
    localStorage.lang=lang;
}
