var hljs = new function() {
    function a(a) {
        return a.replace(/&/gm, "&amp;").replace(/</gm, "&lt;").replace(/>/gm, "&gt;");
    }
    function b(a) {
        return a.nodeName.toLowerCase();
    }
    function c(a, b) {
        var c = a && a.exec(b);
        return c && 0 == c.index;
    }
    function d(a) {
        var b = (a.className + " " + (a.parentNode ? a.parentNode.className : "")).split(/\s+/);
        return b = b.map(function(a) {
            return a.replace(/^lang(uage)?-/, "");
        }), b.filter(function(a) {
            return r(a) || "no-highlight" == a;
        })[0];
    }
    function e(a, b) {
        var c = {};
        for (var d in a) c[d] = a[d];
        if (b) for (var d in b) c[d] = b[d];
        return c;
    }
    function f(a) {
        var c = [];
        return function d(a, e) {
            for (var f = a.firstChild; f; f = f.nextSibling) 3 == f.nodeType ? e += f.nodeValue.length : "br" == b(f) ? e += 1 : 1 == f.nodeType && (c.push({
                event: "start",
                offset: e,
                node: f
            }), e = d(f, e), c.push({
                event: "stop",
                offset: e,
                node: f
            }));
            return e;
        }(a, 0), c;
    }
    function g(c, d, e) {
        function f() {
            return c.length && d.length ? c[0].offset != d[0].offset ? c[0].offset < d[0].offset ? c : d : "start" == d[0].event ? c : d : c.length ? c : d;
        }
        function g(c) {
            function d(b) {
                return " " + b.nodeName + '="' + a(b.value) + '"';
            }
            k += "<" + b(c) + Array.prototype.map.call(c.attributes, d).join("") + ">";
        }
        function h(a) {
            k += "</" + b(a) + ">";
        }
        function i(a) {
            ("start" == a.event ? g : h)(a.node);
        }
        for (var j = 0, k = "", l = []; c.length || d.length; ) {
            var m = f();
            if (k += a(e.substr(j, m[0].offset - j)), j = m[0].offset, m == c) {
                l.reverse().forEach(h);
                do i(m.splice(0, 1)[0]), m = f(); while (m == c && m.length && m[0].offset == j);
                l.reverse().forEach(g);
            } else "start" == m[0].event ? l.push(m[0].node) : l.pop(), i(m.splice(0, 1)[0]);
        }
        return k + a(e.substr(j));
    }
    function h(a) {
        function b(a) {
            return a && a.source || a;
        }
        function c(c, d) {
            return RegExp(b(c), "m" + (a.cI ? "i" : "") + (d ? "g" : ""));
        }
        function d(f, g) {
            if (!f.compiled) {
                if (f.compiled = !0, f.k = f.k || f.bK, f.k) {
                    var h = {}, i = function(b, c) {
                        a.cI && (c = c.toLowerCase()), c.split(" ").forEach(function(a) {
                            var c = a.split("|");
                            h[c[0]] = [ b, c[1] ? Number(c[1]) : 1 ];
                        });
                    };
                    "string" == typeof f.k ? i("keyword", f.k) : Object.keys(f.k).forEach(function(a) {
                        i(a, f.k[a]);
                    }), f.k = h;
                }
                f.lR = c(f.l || /\b[A-Za-z0-9_]+\b/, !0), g && (f.bK && (f.b = "\\b(" + f.bK.split(" ").join("|") + ")\\b"), 
                f.b || (f.b = /\B|\b/), f.bR = c(f.b), f.e || f.eW || (f.e = /\B|\b/), f.e && (f.eR = c(f.e)), 
                f.tE = b(f.e) || "", f.eW && g.tE && (f.tE += (f.e ? "|" : "") + g.tE)), f.i && (f.iR = c(f.i)), 
                void 0 === f.r && (f.r = 1), f.c || (f.c = []);
                var j = [];
                f.c.forEach(function(a) {
                    a.v ? a.v.forEach(function(b) {
                        j.push(e(a, b));
                    }) : j.push("self" == a ? f : a);
                }), f.c = j, f.c.forEach(function(a) {
                    d(a, f);
                }), f.starts && d(f.starts, g);
                var k = f.c.map(function(a) {
                    return a.bK ? "\\.?(" + a.b + ")\\.?" : a.b;
                }).concat([ f.tE, f.i ]).map(b).filter(Boolean);
                f.t = k.length ? c(k.join("|"), !0) : {
                    exec: function() {
                        return null;
                    }
                }, f.continuation = {};
            }
        }
        d(a);
    }
    function i(b, d, e, f) {
        function g(a, b) {
            for (var d = 0; d < b.c.length; d++) if (c(b.c[d].bR, a)) return b.c[d];
        }
        function k(a, b) {
            return c(a.eR, b) ? a : a.eW ? k(a.parent, b) : void 0;
        }
        function l(a, b) {
            return !e && c(b.iR, a);
        }
        function m(a, b) {
            var c = w.cI ? b[0].toLowerCase() : b[0];
            return a.k.hasOwnProperty(c) && a.k[c];
        }
        function n(a, b, c, d) {
            var e = d ? "" : s.classPrefix, f = '<span class="' + e, g = c ? "" : "</span>";
            return f += a + '">', f + b + g;
        }
        function o() {
            if (!x.k) return a(A);
            var b = "", c = 0;
            x.lR.lastIndex = 0;
            for (var d = x.lR.exec(A); d; ) {
                b += a(A.substr(c, d.index - c));
                var e = m(x, d);
                e ? (B += e[1], b += n(e[0], a(d[0]))) : b += a(d[0]), c = x.lR.lastIndex, d = x.lR.exec(A);
            }
            return b + a(A.substr(c));
        }
        function p() {
            if (x.sL && !t[x.sL]) return a(A);
            var b = x.sL ? i(x.sL, A, !0, x.continuation.top) : j(A);
            return x.r > 0 && (B += b.r), "continuous" == x.subLanguageMode && (x.continuation.top = b.top), 
            n(b.language, b.value, !1, !0);
        }
        function q() {
            return void 0 !== x.sL ? p() : o();
        }
        function u(b, c) {
            var d = b.cN ? n(b.cN, "", !0) : "";
            b.rB ? (y += d, A = "") : b.eB ? (y += a(c) + d, A = "") : (y += d, A = c), x = Object.create(b, {
                parent: {
                    value: x
                }
            });
        }
        function v(b, c) {
            if (A += b, void 0 === c) return y += q(), 0;
            var d = g(c, x);
            if (d) return y += q(), u(d, c), d.rB ? 0 : c.length;
            var e = k(x, c);
            if (e) {
                var f = x;
                f.rE || f.eE || (A += c), y += q();
                do x.cN && (y += "</span>"), B += x.r, x = x.parent; while (x != e.parent);
                return f.eE && (y += a(c)), A = "", e.starts && u(e.starts, ""), f.rE ? 0 : c.length;
            }
            if (l(c, x)) throw new Error('Illegal lexeme "' + c + '" for mode "' + (x.cN || "<unnamed>") + '"');
            return A += c, c.length || 1;
        }
        var w = r(b);
        if (!w) throw new Error('Unknown language: "' + b + '"');
        h(w);
        for (var x = f || w, y = "", z = x; z != w; z = z.parent) z.cN && (y += n(z.cN, y, !0));
        var A = "", B = 0;
        try {
            for (var C, D, E = 0; ;) {
                if (x.t.lastIndex = E, C = x.t.exec(d), !C) break;
                D = v(d.substr(E, C.index - E), C[0]), E = C.index + D;
            }
            v(d.substr(E));
            for (var z = x; z.parent; z = z.parent) z.cN && (y += "</span>");
            return {
                r: B,
                value: y,
                language: b,
                top: x
            };
        } catch (F) {
            if (-1 != F.message.indexOf("Illegal")) return {
                r: 0,
                value: a(d)
            };
            throw F;
        }
    }
    function j(b, c) {
        c = c || s.languages || Object.keys(t);
        var d = {
            r: 0,
            value: a(b)
        }, e = d;
        return c.forEach(function(a) {
            if (r(a)) {
                var c = i(a, b, !1);
                c.language = a, c.r > e.r && (e = c), c.r > d.r && (e = d, d = c);
            }
        }), e.language && (d.second_best = e), d;
    }
    function k(a) {
        return s.tabReplace && (a = a.replace(/^((<[^>]+>|\t)+)/gm, function(a, b) {
            return b.replace(/\t/g, s.tabReplace);
        })), s.useBR && (a = a.replace(/\n/g, "<br>")), a;
    }
    function l(a) {
        var b = s.useBR ? a.innerHTML.replace(/\n/g, "").replace(/<br>|<br [^>]*>/g, "\n").replace(/<[^>]*>/g, "") : a.textContent, c = d(a);
        if ("no-highlight" != c) {
            var e = c ? i(c, b, !0) : j(b), h = f(a);
            if (h.length) {
                var l = document.createElementNS("http://www.w3.org/1999/xhtml", "pre");
                l.innerHTML = e.value, e.value = g(h, f(l), b);
            }
            e.value = k(e.value), a.innerHTML = e.value, a.className += " hljs " + (!c && e.language || ""), 
            a.result = {
                language: e.language,
                re: e.r
            }, e.second_best && (a.second_best = {
                language: e.second_best.language,
                re: e.second_best.r
            });
        }
    }
    function m(a) {
        s = e(s, a);
    }
    function n() {
        if (!n.called) {
            n.called = !0;
            var a = document.querySelectorAll("pre code");
            Array.prototype.forEach.call(a, l);
        }
    }
    function o() {
        addEventListener("DOMContentLoaded", n, !1), addEventListener("load", n, !1);
    }
    function p(a, b) {
        var c = t[a] = b(this);
        c.aliases && c.aliases.forEach(function(b) {
            u[b] = a;
        });
    }
    function q() {
        return Object.keys(t);
    }
    function r(a) {
        return t[a] || t[u[a]];
    }
    var s = {
        classPrefix: "hljs-",
        tabReplace: null,
        useBR: !1,
        languages: void 0
    }, t = {}, u = {};
    this.highlight = i, this.highlightAuto = j, this.fixMarkup = k, this.highlightBlock = l, 
    this.configure = m, this.initHighlighting = n, this.initHighlightingOnLoad = o, 
    this.registerLanguage = p, this.listLanguages = q, this.getLanguage = r, this.inherit = e, 
    this.IR = "[a-zA-Z][a-zA-Z0-9_]*", this.UIR = "[a-zA-Z_][a-zA-Z0-9_]*", this.NR = "\\b\\d+(\\.\\d+)?", 
    this.CNR = "(\\b0[xX][a-fA-F0-9]+|(\\b\\d+(\\.\\d*)?|\\.\\d+)([eE][-+]?\\d+)?)", 
    this.BNR = "\\b(0b[01]+)", this.RSR = "!|!=|!==|%|%=|&|&&|&=|\\*|\\*=|\\+|\\+=|,|-|-=|/=|/|:|;|<<|<<=|<=|<|===|==|=|>>>=|>>=|>=|>>>|>>|>|\\?|\\[|\\{|\\(|\\^|\\^=|\\||\\|=|\\|\\||~", 
    this.BE = {
        b: "\\\\[\\s\\S]",
        r: 0
    }, this.ASM = {
        cN: "string",
        b: "'",
        e: "'",
        i: "\\n",
        c: [ this.BE ]
    }, this.QSM = {
        cN: "string",
        b: '"',
        e: '"',
        i: "\\n",
        c: [ this.BE ]
    }, this.PWM = {
        b: /\b(a|an|the|are|I|I'm|isn't|don't|doesn't|won't|but|just|should|pretty|simply|enough|gonna|going|wtf|so|such)\b/
    }, this.CLCM = {
        cN: "comment",
        b: "//",
        e: "$",
        c: [ this.PWM ]
    }, this.CBCM = {
        cN: "comment",
        b: "/\\*",
        e: "\\*/",
        c: [ this.PWM ]
    }, this.HCM = {
        cN: "comment",
        b: "#",
        e: "$",
        c: [ this.PWM ]
    }, this.NM = {
        cN: "number",
        b: this.NR,
        r: 0
    }, this.CNM = {
        cN: "number",
        b: this.CNR,
        r: 0
    }, this.BNM = {
        cN: "number",
        b: this.BNR,
        r: 0
    }, this.CSSNM = {
        cN: "number",
        b: this.NR + "(%|em|ex|ch|rem|vw|vh|vmin|vmax|cm|mm|in|pt|pc|px|deg|grad|rad|turn|s|ms|Hz|kHz|dpi|dpcm|dppx)?",
        r: 0
    }, this.RM = {
        cN: "regexp",
        b: /\//,
        e: /\/[gim]*/,
        i: /\n/,
        c: [ this.BE, {
            b: /\[/,
            e: /\]/,
            r: 0,
            c: [ this.BE ]
        } ]
    }, this.TM = {
        cN: "title",
        b: this.IR,
        r: 0
    }, this.UTM = {
        cN: "title",
        b: this.UIR,
        r: 0
    };
}();

hljs.registerLanguage("bash", function(a) {
    var b = {
        cN: "variable",
        v: [ {
            b: /\$[\w\d#@][\w\d_]*/
        }, {
            b: /\$\{(.*?)\}/
        } ]
    }, c = {
        cN: "string",
        b: /"/,
        e: /"/,
        c: [ a.BE, b, {
            cN: "variable",
            b: /\$\(/,
            e: /\)/,
            c: [ a.BE ]
        } ]
    }, d = {
        cN: "string",
        b: /'/,
        e: /'/
    };
    return {
        aliases: [ "sh", "zsh" ],
        l: /-?[a-z\.]+/,
        k: {
            keyword: "if then else elif fi for break continue while in do done exit return set declare case esac export exec",
            literal: "true false",
            built_in: "printf echo read cd pwd pushd popd dirs let eval unset typeset readonly getopts source shopt caller type hash bind help sudo",
            operator: "-ne -eq -lt -gt -f -d -e -s -l -a"
        },
        c: [ {
            cN: "shebang",
            b: /^#![^\n]+sh\s*$/,
            r: 10
        }, {
            cN: "function",
            b: /\w[\w\d_]*\s*\(\s*\)\s*\{/,
            rB: !0,
            c: [ a.inherit(a.TM, {
                b: /\w[\w\d_]*/
            }) ],
            r: 0
        }, a.HCM, a.NM, c, d, b ]
    };
}), hljs.registerLanguage("cs", function(a) {
    var b = "abstract as base bool break byte case catch char checked const continue decimal default delegate do double else enum event explicit extern false finally fixed float for foreach goto if implicit in int interface internal is lock long new null object operator out override params private protected public readonly ref return sbyte sealed short sizeof stackalloc static string struct switch this throw true try typeof uint ulong unchecked unsafe ushort using virtual volatile void while async await ascending descending from get group into join let orderby partial select set value var where yield";
    return {
        aliases: [ "csharp" ],
        k: b,
        i: /::/,
        c: [ {
            cN: "comment",
            b: "///",
            e: "$",
            rB: !0,
            c: [ {
                cN: "xmlDocTag",
                v: [ {
                    b: "///",
                    r: 0
                }, {
                    b: "<!--|-->"
                }, {
                    b: "</?",
                    e: ">"
                } ]
            } ]
        }, a.CLCM, a.CBCM, {
            cN: "preprocessor",
            b: "#",
            e: "$",
            k: "if else elif endif define undef warning error line region endregion pragma checksum"
        }, {
            cN: "string",
            b: '@"',
            e: '"',
            c: [ {
                b: '""'
            } ]
        }, a.ASM, a.QSM, a.CNM, {
            bK: "protected public private internal",
            e: /[{;=]/,
            k: b,
            c: [ {
                bK: "class namespace interface",
                starts: {
                    c: [ a.TM ]
                }
            }, {
                b: a.IR + "\\s*\\(",
                rB: !0,
                c: [ a.TM ]
            } ]
        } ]
    };
}), hljs.registerLanguage("ruby", function(a) {
    var b = "[a-zA-Z_]\\w*[!?=]?|[-+~]\\@|<<|>>|=~|===?|<=>|[<>]=?|\\*\\*|[-/+%^&*~`|]|\\[\\]=?", c = "and false then defined module in return redo if BEGIN retry end for true self when next until do begin unless END rescue nil else break undef not super class case require yield alias while ensure elsif or include attr_reader attr_writer attr_accessor", d = {
        cN: "yardoctag",
        b: "@[A-Za-z]+"
    }, e = {
        cN: "value",
        b: "#<",
        e: ">"
    }, f = {
        cN: "comment",
        v: [ {
            b: "#",
            e: "$",
            c: [ d ]
        }, {
            b: "^\\=begin",
            e: "^\\=end",
            c: [ d ],
            r: 10
        }, {
            b: "^__END__",
            e: "\\n$"
        } ]
    }, g = {
        cN: "subst",
        b: "#\\{",
        e: "}",
        k: c
    }, h = {
        cN: "string",
        c: [ a.BE, g ],
        v: [ {
            b: /'/,
            e: /'/
        }, {
            b: /"/,
            e: /"/
        }, {
            b: "%[qw]?\\(",
            e: "\\)"
        }, {
            b: "%[qw]?\\[",
            e: "\\]"
        }, {
            b: "%[qw]?{",
            e: "}"
        }, {
            b: "%[qw]?<",
            e: ">"
        }, {
            b: "%[qw]?/",
            e: "/"
        }, {
            b: "%[qw]?%",
            e: "%"
        }, {
            b: "%[qw]?-",
            e: "-"
        }, {
            b: "%[qw]?\\|",
            e: "\\|"
        }, {
            b: /\B\?(\\\d{1,3}|\\x[A-Fa-f0-9]{1,2}|\\u[A-Fa-f0-9]{4}|\\?\S)\b/
        } ]
    }, i = {
        cN: "params",
        b: "\\(",
        e: "\\)",
        k: c
    }, j = [ h, e, f, {
        cN: "class",
        bK: "class module",
        e: "$|;",
        i: /=/,
        c: [ a.inherit(a.TM, {
            b: "[A-Za-z_]\\w*(::\\w+)*(\\?|\\!)?"
        }), {
            cN: "inheritance",
            b: "<\\s*",
            c: [ {
                cN: "parent",
                b: "(" + a.IR + "::)?" + a.IR
            } ]
        }, f ]
    }, {
        cN: "function",
        bK: "def",
        e: " |$|;",
        r: 0,
        c: [ a.inherit(a.TM, {
            b: b
        }), i, f ]
    }, {
        cN: "constant",
        b: "(::)?(\\b[A-Z]\\w*(::)?)+",
        r: 0
    }, {
        cN: "symbol",
        b: ":",
        c: [ h, {
            b: b
        } ],
        r: 0
    }, {
        cN: "symbol",
        b: a.UIR + "(\\!|\\?)?:",
        r: 0
    }, {
        cN: "number",
        b: "(\\b0[0-7_]+)|(\\b0x[0-9a-fA-F_]+)|(\\b[1-9][0-9_]*(\\.[0-9_]+)?)|[0_]\\b",
        r: 0
    }, {
        cN: "variable",
        b: "(\\$\\W)|((\\$|\\@\\@?)(\\w+))"
    }, {
        b: "(" + a.RSR + ")\\s*",
        c: [ e, f, {
            cN: "regexp",
            c: [ a.BE, g ],
            i: /\n/,
            v: [ {
                b: "/",
                e: "/[a-z]*"
            }, {
                b: "%r{",
                e: "}[a-z]*"
            }, {
                b: "%r\\(",
                e: "\\)[a-z]*"
            }, {
                b: "%r!",
                e: "![a-z]*"
            }, {
                b: "%r\\[",
                e: "\\][a-z]*"
            } ]
        } ],
        r: 0
    } ];
    g.c = j, i.c = j;
    var k = [ {
        r: 1,
        cN: "output",
        b: "^\\s*=> ",
        e: "$",
        rB: !0,
        c: [ {
            cN: "status",
            b: "^\\s*=>"
        }, {
            b: " ",
            e: "$",
            c: j
        } ]
    }, {
        r: 1,
        cN: "input",
        b: "^[^ ][^=>]*>+ ",
        e: "$",
        rB: !0,
        c: [ {
            cN: "prompt",
            b: "^[^ ][^=>]*>+"
        }, {
            b: " ",
            e: "$",
            c: j
        } ]
    } ];
    return {
        aliases: [ "rb", "gemspec", "podspec", "thor", "irb" ],
        k: c,
        c: k.concat(j)
    };
}), hljs.registerLanguage("diff", function() {
    return {
        aliases: [ "patch" ],
        c: [ {
            cN: "chunk",
            r: 10,
            v: [ {
                b: /^\@\@ +\-\d+,\d+ +\+\d+,\d+ +\@\@$/
            }, {
                b: /^\*\*\* +\d+,\d+ +\*\*\*\*$/
            }, {
                b: /^\-\-\- +\d+,\d+ +\-\-\-\-$/
            } ]
        }, {
            cN: "header",
            v: [ {
                b: /Index: /,
                e: /$/
            }, {
                b: /=====/,
                e: /=====$/
            }, {
                b: /^\-\-\-/,
                e: /$/
            }, {
                b: /^\*{3} /,
                e: /$/
            }, {
                b: /^\+\+\+/,
                e: /$/
            }, {
                b: /\*{5}/,
                e: /\*{5}$/
            } ]
        }, {
            cN: "addition",
            b: "^\\+",
            e: "$"
        }, {
            cN: "deletion",
            b: "^\\-",
            e: "$"
        }, {
            cN: "change",
            b: "^\\!",
            e: "$"
        } ]
    };
}), hljs.registerLanguage("javascript", function(a) {
    return {
        aliases: [ "js" ],
        k: {
            keyword: "in if for while finally var new function do return void else break catch instanceof with throw case default try this switch continue typeof delete let yield const class",
            literal: "true false null undefined NaN Infinity",
            built_in: "eval isFinite isNaN parseFloat parseInt decodeURI decodeURIComponent encodeURI encodeURIComponent escape unescape Object Function Boolean Error EvalError InternalError RangeError ReferenceError StopIteration SyntaxError TypeError URIError Number Math Date String RegExp Array Float32Array Float64Array Int16Array Int32Array Int8Array Uint16Array Uint32Array Uint8Array Uint8ClampedArray ArrayBuffer DataView JSON Intl arguments require module console window document"
        },
        c: [ {
            cN: "pi",
            b: /^\s*('|")use strict('|")/,
            r: 10
        }, a.ASM, a.QSM, a.CLCM, a.CBCM, a.CNM, {
            b: "(" + a.RSR + "|\\b(case|return|throw)\\b)\\s*",
            k: "return throw case",
            c: [ a.CLCM, a.CBCM, a.RM, {
                b: /</,
                e: />;/,
                r: 0,
                sL: "xml"
            } ],
            r: 0
        }, {
            cN: "function",
            bK: "function",
            e: /\{/,
            eE: !0,
            c: [ a.inherit(a.TM, {
                b: /[A-Za-z$_][0-9A-Za-z$_]*/
            }), {
                cN: "params",
                b: /\(/,
                e: /\)/,
                c: [ a.CLCM, a.CBCM ],
                i: /["'\(]/
            } ],
            i: /\[|%/
        }, {
            b: /\$[(.]/
        }, {
            b: "\\." + a.IR,
            r: 0
        } ]
    };
}), hljs.registerLanguage("xml", function() {
    var a = "[A-Za-z0-9\\._:-]+", b = {
        b: /<\?(php)?(?!\w)/,
        e: /\?>/,
        sL: "php",
        subLanguageMode: "continuous"
    }, c = {
        eW: !0,
        i: /</,
        r: 0,
        c: [ b, {
            cN: "attribute",
            b: a,
            r: 0
        }, {
            b: "=",
            r: 0,
            c: [ {
                cN: "value",
                v: [ {
                    b: /"/,
                    e: /"/
                }, {
                    b: /'/,
                    e: /'/
                }, {
                    b: /[^\s\/>]+/
                } ]
            } ]
        } ]
    };
    return {
        aliases: [ "html", "xhtml", "rss", "atom", "xsl", "plist" ],
        cI: !0,
        c: [ {
            cN: "doctype",
            b: "<!DOCTYPE",
            e: ">",
            r: 10,
            c: [ {
                b: "\\[",
                e: "\\]"
            } ]
        }, {
            cN: "comment",
            b: "<!--",
            e: "-->",
            r: 10
        }, {
            cN: "cdata",
            b: "<\\!\\[CDATA\\[",
            e: "\\]\\]>",
            r: 10
        }, {
            cN: "tag",
            b: "<style(?=\\s|>|$)",
            e: ">",
            k: {
                title: "style"
            },
            c: [ c ],
            starts: {
                e: "</style>",
                rE: !0,
                sL: "css"
            }
        }, {
            cN: "tag",
            b: "<script(?=\\s|>|$)",
            e: ">",
            k: {
                title: "script"
            },
            c: [ c ],
            starts: {
                e: "</script>",
                rE: !0,
                sL: "javascript"
            }
        }, {
            b: "<%",
            e: "%>",
            sL: "vbscript"
        }, b, {
            cN: "pi",
            b: /<\?\w+/,
            e: /\?>/,
            r: 10
        }, {
            cN: "tag",
            b: "</?",
            e: "/?>",
            c: [ {
                cN: "title",
                b: "[^ /><]+",
                r: 0
            }, c ]
        } ]
    };
}), hljs.registerLanguage("markdown", function() {
    return {
        aliases: [ "md", "mkdown", "mkd" ],
        c: [ {
            cN: "header",
            v: [ {
                b: "^#{1,6}",
                e: "$"
            }, {
                b: "^.+?\\n[=-]{2,}$"
            } ]
        }, {
            b: "<",
            e: ">",
            sL: "xml",
            r: 0
        }, {
            cN: "bullet",
            b: "^([*+-]|(\\d+\\.))\\s+"
        }, {
            cN: "strong",
            b: "[*_]{2}.+?[*_]{2}"
        }, {
            cN: "emphasis",
            v: [ {
                b: "\\*.+?\\*"
            }, {
                b: "_.+?_",
                r: 0
            } ]
        }, {
            cN: "blockquote",
            b: "^>\\s+",
            e: "$"
        }, {
            cN: "code",
            v: [ {
                b: "`.+?`"
            }, {
                b: "^( {4}|	)",
                e: "$",
                r: 0
            } ]
        }, {
            cN: "horizontal_rule",
            b: "^[-\\*]{3,}",
            e: "$"
        }, {
            b: "\\[.+?\\][\\(\\[].+?[\\)\\]]",
            rB: !0,
            c: [ {
                cN: "link_label",
                b: "\\[",
                e: "\\]",
                eB: !0,
                rE: !0,
                r: 0
            }, {
                cN: "link_url",
                b: "\\]\\(",
                e: "\\)",
                eB: !0,
                eE: !0
            }, {
                cN: "link_reference",
                b: "\\]\\[",
                e: "\\]",
                eB: !0,
                eE: !0
            } ],
            r: 10
        }, {
            b: "^\\[.+\\]:",
            e: "$",
            rB: !0,
            c: [ {
                cN: "link_reference",
                b: "\\[",
                e: "\\]",
                eB: !0,
                eE: !0
            }, {
                cN: "link_url",
                b: "\\s",
                e: "$"
            } ]
        } ]
    };
}), hljs.registerLanguage("css", function(a) {
    var b = "[a-zA-Z-][a-zA-Z0-9_-]*", c = {
        cN: "function",
        b: b + "\\(",
        rB: !0,
        eE: !0,
        e: "\\("
    };
    return {
        cI: !0,
        i: "[=/|']",
        c: [ a.CBCM, {
            cN: "id",
            b: "\\#[A-Za-z0-9_-]+"
        }, {
            cN: "class",
            b: "\\.[A-Za-z0-9_-]+",
            r: 0
        }, {
            cN: "attr_selector",
            b: "\\[",
            e: "\\]",
            i: "$"
        }, {
            cN: "pseudo",
            b: ":(:)?[a-zA-Z0-9\\_\\-\\+\\(\\)\\\"\\']+"
        }, {
            cN: "at_rule",
            b: "@(font-face|page)",
            l: "[a-z-]+",
            k: "font-face page"
        }, {
            cN: "at_rule",
            b: "@",
            e: "[{;]",
            c: [ {
                cN: "keyword",
                b: /\S+/
            }, {
                b: /\s/,
                eW: !0,
                eE: !0,
                r: 0,
                c: [ c, a.ASM, a.QSM, a.CSSNM ]
            } ]
        }, {
            cN: "tag",
            b: b,
            r: 0
        }, {
            cN: "rules",
            b: "{",
            e: "}",
            i: "[^\\s]",
            r: 0,
            c: [ a.CBCM, {
                cN: "rule",
                b: "[^\\s]",
                rB: !0,
                e: ";",
                eW: !0,
                c: [ {
                    cN: "attribute",
                    b: "[A-Z\\_\\.\\-]+",
                    e: ":",
                    eE: !0,
                    i: "[^\\s]",
                    starts: {
                        cN: "value",
                        eW: !0,
                        eE: !0,
                        c: [ c, a.CSSNM, a.QSM, a.ASM, a.CBCM, {
                            cN: "hexcolor",
                            b: "#[0-9A-Fa-f]+"
                        }, {
                            cN: "important",
                            b: "!important"
                        } ]
                    }
                } ]
            } ]
        } ]
    };
}), hljs.registerLanguage("http", function() {
    return {
        i: "\\S",
        c: [ {
            cN: "status",
            b: "^HTTP/[0-9\\.]+",
            e: "$",
            c: [ {
                cN: "number",
                b: "\\b\\d{3}\\b"
            } ]
        }, {
            cN: "request",
            b: "^[A-Z]+ (.*?) HTTP/[0-9\\.]+$",
            rB: !0,
            e: "$",
            c: [ {
                cN: "string",
                b: " ",
                e: " ",
                eB: !0,
                eE: !0
            } ]
        }, {
            cN: "attribute",
            b: "^\\w",
            e: ": ",
            eE: !0,
            i: "\\n|\\s|=",
            starts: {
                cN: "string",
                e: "$"
            }
        }, {
            b: "\\n\\n",
            starts: {
                sL: "",
                eW: !0
            }
        } ]
    };
}), hljs.registerLanguage("java", function(a) {
    var b = "false synchronized int abstract float private char boolean static null if const for true while long throw strictfp finally protected import native final return void enum else break transient new catch instanceof byte super volatile case assert short package default double public try this switch continue throws";
    return {
        aliases: [ "jsp" ],
        k: b,
        i: /<\//,
        c: [ {
            cN: "javadoc",
            b: "/\\*\\*",
            e: "\\*/",
            c: [ {
                cN: "javadoctag",
                b: "(^|\\s)@[A-Za-z]+"
            } ],
            r: 10
        }, a.CLCM, a.CBCM, a.ASM, a.QSM, {
            bK: "protected public private",
            e: /[{;=]/,
            k: b,
            c: [ {
                cN: "class",
                bK: "class interface",
                eW: !0,
                eE: !0,
                i: /[:"\[\]]/,
                c: [ {
                    bK: "extends implements",
                    r: 10
                }, a.UTM ]
            }, {
                b: a.UIR + "\\s*\\(",
                rB: !0,
                c: [ a.UTM ]
            } ]
        }, a.CNM, {
            cN: "annotation",
            b: "@[A-Za-z]+"
        } ]
    };
}), hljs.registerLanguage("php", function(a) {
    var b = {
        cN: "variable",
        b: "(\\$|->)+[a-zA-Z_-ÿ][a-zA-Z0-9_-ÿ]*"
    }, c = {
        cN: "preprocessor",
        b: /<\?(php)?|\?>/
    }, d = {
        cN: "string",
        c: [ a.BE, c ],
        v: [ {
            b: 'b"',
            e: '"'
        }, {
            b: "b'",
            e: "'"
        }, a.inherit(a.ASM, {
            i: null
        }), a.inherit(a.QSM, {
            i: null
        }) ]
    }, e = {
        v: [ a.BNM, a.CNM ]
    };
    return {
        aliases: [ "php3", "php4", "php5", "php6" ],
        cI: !0,
        k: "and include_once list abstract global private echo interface as static endswitch array null if endwhile or const for endforeach self var while isset public protected exit foreach throw elseif include __FILE__ empty require_once do xor return parent clone use __CLASS__ __LINE__ else break print eval new catch __METHOD__ case exception default die require __FUNCTION__ enddeclare final try switch continue endfor endif declare unset true false trait goto instanceof insteadof __DIR__ __NAMESPACE__ yield finally",
        c: [ a.CLCM, a.HCM, {
            cN: "comment",
            b: "/\\*",
            e: "\\*/",
            c: [ {
                cN: "phpdoc",
                b: "\\s@[A-Za-z]+"
            }, c ]
        }, {
            cN: "comment",
            b: "__halt_compiler.+?;",
            eW: !0,
            k: "__halt_compiler",
            l: a.UIR
        }, {
            cN: "string",
            b: "<<<['\"]?\\w+['\"]?$",
            e: "^\\w+;",
            c: [ a.BE ]
        }, c, b, {
            cN: "function",
            bK: "function",
            e: /[;{]/,
            eE: !0,
            i: "\\$|\\[|%",
            c: [ a.UTM, {
                cN: "params",
                b: "\\(",
                e: "\\)",
                c: [ "self", b, a.CBCM, d, e ]
            } ]
        }, {
            cN: "class",
            bK: "class interface",
            e: "{",
            eE: !0,
            i: /[:\(\$"]/,
            c: [ {
                bK: "extends implements",
                r: 10
            }, a.UTM ]
        }, {
            bK: "namespace",
            e: ";",
            i: /[\.']/,
            c: [ a.UTM ]
        }, {
            bK: "use",
            e: ";",
            c: [ a.UTM ]
        }, {
            b: "=>"
        }, d, e ]
    };
}), hljs.registerLanguage("python", function(a) {
    var b = {
        cN: "prompt",
        b: /^(>>>|\.\.\.) /
    }, c = {
        cN: "string",
        c: [ a.BE ],
        v: [ {
            b: /(u|b)?r?'''/,
            e: /'''/,
            c: [ b ],
            r: 10
        }, {
            b: /(u|b)?r?"""/,
            e: /"""/,
            c: [ b ],
            r: 10
        }, {
            b: /(u|r|ur)'/,
            e: /'/,
            r: 10
        }, {
            b: /(u|r|ur)"/,
            e: /"/,
            r: 10
        }, {
            b: /(b|br)'/,
            e: /'/
        }, {
            b: /(b|br)"/,
            e: /"/
        }, a.ASM, a.QSM ]
    }, d = {
        cN: "number",
        r: 0,
        v: [ {
            b: a.BNR + "[lLjJ]?"
        }, {
            b: "\\b(0o[0-7]+)[lLjJ]?"
        }, {
            b: a.CNR + "[lLjJ]?"
        } ]
    }, e = {
        cN: "params",
        b: /\(/,
        e: /\)/,
        c: [ "self", b, d, c ]
    }, f = {
        e: /:/,
        i: /[${=;\n]/,
        c: [ a.UTM, e ]
    };
    return {
        aliases: [ "py", "gyp" ],
        k: {
            keyword: "and elif is global as in if from raise for except finally print import pass return exec else break not with class assert yield try while continue del or def lambda nonlocal|10 None True False",
            built_in: "Ellipsis NotImplemented"
        },
        i: /(<\/|->|\?)/,
        c: [ b, d, c, a.HCM, a.inherit(f, {
            cN: "function",
            bK: "def",
            r: 10
        }), a.inherit(f, {
            cN: "class",
            bK: "class"
        }), {
            cN: "decorator",
            b: /@/,
            e: /$/
        }, {
            b: /\b(print|exec)\(/
        } ]
    };
}), hljs.registerLanguage("sql", function(a) {
    var b = {
        cN: "comment",
        b: "--",
        e: "$"
    };
    return {
        cI: !0,
        i: /[<>]/,
        c: [ {
            cN: "operator",
            bK: "begin end start commit rollback savepoint lock alter create drop rename call delete do handler insert load replace select truncate update set show pragma grant merge describe use explain help declare prepare execute deallocate savepoint release unlock purge reset change stop analyze cache flush optimize repair kill install uninstall checksum restore check backup",
            e: /;/,
            eW: !0,
            k: {
                keyword: "abs absolute acos action add adddate addtime aes_decrypt aes_encrypt after aggregate all allocate alter analyze and any are as asc ascii asin assertion at atan atan2 atn2 authorization authors avg backup before begin benchmark between bin binlog bit_and bit_count bit_length bit_or bit_xor both by cache call cascade cascaded case cast catalog ceil ceiling chain change changed char_length character_length charindex charset check checksum checksum_agg choose close coalesce coercibility collate collation collationproperty column columns columns_updated commit compress concat concat_ws concurrent connect connection connection_id consistent constraint constraints continue contributors conv convert convert_tz corresponding cos cot count count_big crc32 create cross cume_dist curdate current current_date current_time current_timestamp current_user cursor curtime data database databases datalength date_add date_format date_sub dateadd datediff datefromparts datename datepart datetime2fromparts datetimeoffsetfromparts day dayname dayofmonth dayofweek dayofyear deallocate declare decode default deferrable deferred degrees delayed delete des_decrypt des_encrypt des_key_file desc describe descriptor diagnostics difference disconnect distinct distinctrow div do domain double drop dumpfile each else elt enclosed encode encrypt end end-exec engine engines eomonth errors escape escaped event eventdata events except exception exec execute exists exp explain export_set extended external extract fast fetch field fields find_in_set first first_value floor flush for force foreign format found found_rows from from_base64 from_days from_unixtime full function get get_format get_lock getdate getutcdate global go goto grant grants greatest group group_concat grouping grouping_id gtid_subset gtid_subtract handler having help hex high_priority hosts hour ident_current ident_incr ident_seed identified identity if ifnull ignore iif ilike immediate in index indicator inet6_aton inet6_ntoa inet_aton inet_ntoa infile initially inner innodb input insert install instr intersect into is is_free_lock is_ipv4 is_ipv4_compat is_ipv4_mapped is_not is_not_null is_used_lock isdate isnull isolation join key kill language last last_day last_insert_id last_value lcase lead leading least leaves left len lenght level like limit lines ln load load_file local localtime localtimestamp locate lock log log10 log2 logfile logs low_priority lower lpad ltrim make_set makedate maketime master master_pos_wait match matched max md5 medium merge microsecond mid min minute mod mode module month monthname mutex name_const names national natural nchar next no no_write_to_binlog not now nullif nvarchar oct octet_length of old_password on only open optimize option optionally or ord order outer outfile output pad parse partial partition password patindex percent_rank percentile_cont percentile_disc period_add period_diff pi plugin position pow power pragma precision prepare preserve primary prior privileges procedure procedure_analyze processlist profile profiles public publishingservername purge quarter query quick quote quotename radians rand read references regexp relative relaylog release release_lock rename repair repeat replace replicate reset restore restrict return returns reverse revoke right rlike rollback rollup round row row_count rows rpad rtrim savepoint schema scroll sec_to_time second section select serializable server session session_user set sha sha1 sha2 share show sign sin size slave sleep smalldatetimefromparts snapshot some soname soundex sounds_like space sql sql_big_result sql_buffer_result sql_cache sql_calc_found_rows sql_no_cache sql_small_result sql_variant_property sqlstate sqrt square start starting status std stddev stddev_pop stddev_samp stdev stdevp stop str str_to_date straight_join strcmp string stuff subdate substr substring subtime subtring_index sum switchoffset sysdate sysdatetime sysdatetimeoffset system_user sysutcdatetime table tables tablespace tan temporary terminated tertiary_weights then time time_format time_to_sec timediff timefromparts timestamp timestampadd timestampdiff timezone_hour timezone_minute to to_base64 to_days to_seconds todatetimeoffset trailing transaction translation trigger trigger_nestlevel triggers trim truncate try_cast try_convert try_parse ucase uncompress uncompressed_length unhex unicode uninstall union unique unix_timestamp unknown unlock update upgrade upped upper usage use user user_resources using utc_date utc_time utc_timestamp uuid uuid_short validate_password_strength value values var var_pop var_samp variables variance varp version view warnings week weekday weekofyear weight_string when whenever where with work write xml xor year yearweek zon",
                literal: "true false null",
                built_in: "array bigint binary bit blob boolean char character date dec decimal float int integer interval number numeric real serial smallint varchar varying int8 serial8 text"
            },
            c: [ {
                cN: "string",
                b: "'",
                e: "'",
                c: [ a.BE, {
                    b: "''"
                } ]
            }, {
                cN: "string",
                b: '"',
                e: '"',
                c: [ a.BE, {
                    b: '""'
                } ]
            }, {
                cN: "string",
                b: "`",
                e: "`",
                c: [ a.BE ]
            }, a.CNM, a.CBCM, b ]
        }, a.CBCM, b ]
    };
}), hljs.registerLanguage("ini", function(a) {
    return {
        cI: !0,
        i: /\S/,
        c: [ {
            cN: "comment",
            b: ";",
            e: "$"
        }, {
            cN: "title",
            b: "^\\[",
            e: "\\]"
        }, {
            cN: "setting",
            b: "^[a-z0-9\\[\\]_-]+[ \\t]*=[ \\t]*",
            e: "$",
            c: [ {
                cN: "value",
                eW: !0,
                k: "on off true false yes no",
                c: [ a.QSM, a.NM ],
                r: 0
            } ]
        } ]
    };
}), hljs.registerLanguage("perl", function(a) {
    var b = "getpwent getservent quotemeta msgrcv scalar kill dbmclose undef lc ma syswrite tr send umask sysopen shmwrite vec qx utime local oct semctl localtime readpipe do return format read sprintf dbmopen pop getpgrp not getpwnam rewinddir qqfileno qw endprotoent wait sethostent bless s|0 opendir continue each sleep endgrent shutdown dump chomp connect getsockname die socketpair close flock exists index shmgetsub for endpwent redo lstat msgctl setpgrp abs exit select print ref gethostbyaddr unshift fcntl syscall goto getnetbyaddr join gmtime symlink semget splice x|0 getpeername recv log setsockopt cos last reverse gethostbyname getgrnam study formline endhostent times chop length gethostent getnetent pack getprotoent getservbyname rand mkdir pos chmod y|0 substr endnetent printf next open msgsnd readdir use unlink getsockopt getpriority rindex wantarray hex system getservbyport endservent int chr untie rmdir prototype tell listen fork shmread ucfirst setprotoent else sysseek link getgrgid shmctl waitpid unpack getnetbyname reset chdir grep split require caller lcfirst until warn while values shift telldir getpwuid my getprotobynumber delete and sort uc defined srand accept package seekdir getprotobyname semop our rename seek if q|0 chroot sysread setpwent no crypt getc chown sqrt write setnetent setpriority foreach tie sin msgget map stat getlogin unless elsif truncate exec keys glob tied closedirioctl socket readlink eval xor readline binmode setservent eof ord bind alarm pipe atan2 getgrent exp time push setgrent gt lt or ne m|0 break given say state when", c = {
        cN: "subst",
        b: "[$@]\\{",
        e: "\\}",
        k: b
    }, d = {
        b: "->{",
        e: "}"
    }, e = {
        cN: "variable",
        v: [ {
            b: /\$\d/
        }, {
            b: /[\$\%\@](\^\w\b|#\w+(\:\:\w+)*|{\w+}|\w+(\:\:\w*)*)/
        }, {
            b: /[\$\%\@][^\s\w{]/,
            r: 0
        } ]
    }, f = {
        cN: "comment",
        b: "^(__END__|__DATA__)",
        e: "\\n$",
        r: 5
    }, g = [ a.BE, c, e ], h = [ e, a.HCM, f, {
        cN: "comment",
        b: "^\\=\\w",
        e: "\\=cut",
        eW: !0
    }, d, {
        cN: "string",
        c: g,
        v: [ {
            b: "q[qwxr]?\\s*\\(",
            e: "\\)",
            r: 5
        }, {
            b: "q[qwxr]?\\s*\\[",
            e: "\\]",
            r: 5
        }, {
            b: "q[qwxr]?\\s*\\{",
            e: "\\}",
            r: 5
        }, {
            b: "q[qwxr]?\\s*\\|",
            e: "\\|",
            r: 5
        }, {
            b: "q[qwxr]?\\s*\\<",
            e: "\\>",
            r: 5
        }, {
            b: "qw\\s+q",
            e: "q",
            r: 5
        }, {
            b: "'",
            e: "'",
            c: [ a.BE ]
        }, {
            b: '"',
            e: '"'
        }, {
            b: "`",
            e: "`",
            c: [ a.BE ]
        }, {
            b: "{\\w+}",
            c: [],
            r: 0
        }, {
            b: "-?\\w+\\s*\\=\\>",
            c: [],
            r: 0
        } ]
    }, {
        cN: "number",
        b: "(\\b0[0-7_]+)|(\\b0x[0-9a-fA-F_]+)|(\\b[1-9][0-9_]*(\\.[0-9_]+)?)|[0_]\\b",
        r: 0
    }, {
        b: "(\\/\\/|" + a.RSR + "|\\b(split|return|print|reverse|grep)\\b)\\s*",
        k: "split return print reverse grep",
        r: 0,
        c: [ a.HCM, f, {
            cN: "regexp",
            b: "(s|tr|y)/(\\\\.|[^/])*/(\\\\.|[^/])*/[a-z]*",
            r: 10
        }, {
            cN: "regexp",
            b: "(m|qr)?/",
            e: "/[a-z]*",
            c: [ a.BE ],
            r: 0
        } ]
    }, {
        cN: "sub",
        bK: "sub",
        e: "(\\s*\\(.*?\\))?[;{]",
        r: 5
    }, {
        cN: "operator",
        b: "-\\w\\b",
        r: 0
    } ];
    return c.c = h, d.c = h, {
        aliases: [ "pl" ],
        k: b,
        c: h
    };
}), hljs.registerLanguage("objectivec", function(a) {
    var b = {
        keyword: "int float while char export sizeof typedef const struct for union unsigned long volatile static bool mutable if do return goto void enum else break extern asm case short default double register explicit signed typename this switch continue wchar_t inline readonly assign readwrite self @synchronized id typeof nonatomic super unichar IBOutlet IBAction strong weak copy in out inout bycopy byref oneway __strong __weak __block __autoreleasing @private @protected @public @try @property @end @throw @catch @finally @autoreleasepool @synthesize @dynamic @selector @optional @required",
        literal: "false true FALSE TRUE nil YES NO NULL",
        built_in: "NSString NSDictionary CGRect CGPoint UIButton UILabel UITextView UIWebView MKMapView NSView NSViewController NSWindow NSWindowController NSSet NSUUID NSIndexSet UISegmentedControl NSObject UITableViewDelegate UITableViewDataSource NSThread UIActivityIndicator UITabbar UIToolBar UIBarButtonItem UIImageView NSAutoreleasePool UITableView BOOL NSInteger CGFloat NSException NSLog NSMutableString NSMutableArray NSMutableDictionary NSURL NSIndexPath CGSize UITableViewCell UIView UIViewController UINavigationBar UINavigationController UITabBarController UIPopoverController UIPopoverControllerDelegate UIImage NSNumber UISearchBar NSFetchedResultsController NSFetchedResultsChangeType UIScrollView UIScrollViewDelegate UIEdgeInsets UIColor UIFont UIApplication NSNotFound NSNotificationCenter NSNotification UILocalNotification NSBundle NSFileManager NSTimeInterval NSDate NSCalendar NSUserDefaults UIWindow NSRange NSArray NSError NSURLRequest NSURLConnection UIInterfaceOrientation MPMoviePlayerController dispatch_once_t dispatch_queue_t dispatch_sync dispatch_async dispatch_once"
    }, c = /[a-zA-Z@][a-zA-Z0-9_]*/, d = "@interface @class @protocol @implementation";
    return {
        aliases: [ "m", "mm", "objc", "obj-c" ],
        k: b,
        l: c,
        i: "</",
        c: [ a.CLCM, a.CBCM, a.CNM, a.QSM, {
            cN: "string",
            v: [ {
                b: '@"',
                e: '"',
                i: "\\n",
                c: [ a.BE ]
            }, {
                b: "'",
                e: "[^\\\\]'",
                i: "[^\\\\][^']"
            } ]
        }, {
            cN: "preprocessor",
            b: "#",
            e: "$",
            c: [ {
                cN: "title",
                v: [ {
                    b: '"',
                    e: '"'
                }, {
                    b: "<",
                    e: ">"
                } ]
            } ]
        }, {
            cN: "class",
            b: "(" + d.split(" ").join("|") + ")\\b",
            e: "({|$)",
            eE: !0,
            k: d,
            l: c,
            c: [ a.UTM ]
        }, {
            cN: "variable",
            b: "\\." + a.UIR,
            r: 0
        } ]
    };
}), hljs.registerLanguage("coffeescript", function(a) {
    var b = {
        keyword: "in if for while finally new do return else break catch instanceof throw try this switch continue typeof delete debugger super then unless until loop of by when and or is isnt not",
        literal: "true false null undefined yes no on off",
        reserved: "case default function var void with const let enum export import native __hasProp __extends __slice __bind __indexOf",
        built_in: "npm require console print module global window document"
    }, c = "[A-Za-z$_][0-9A-Za-z$_]*", d = a.inherit(a.TM, {
        b: c
    }), e = {
        cN: "subst",
        b: /#\{/,
        e: /}/,
        k: b
    }, f = [ a.BNM, a.inherit(a.CNM, {
        starts: {
            e: "(\\s*/)?",
            r: 0
        }
    }), {
        cN: "string",
        v: [ {
            b: /'''/,
            e: /'''/,
            c: [ a.BE ]
        }, {
            b: /'/,
            e: /'/,
            c: [ a.BE ]
        }, {
            b: /"""/,
            e: /"""/,
            c: [ a.BE, e ]
        }, {
            b: /"/,
            e: /"/,
            c: [ a.BE, e ]
        } ]
    }, {
        cN: "regexp",
        v: [ {
            b: "///",
            e: "///",
            c: [ e, a.HCM ]
        }, {
            b: "//[gim]*",
            r: 0
        }, {
            b: "/\\S(\\\\.|[^\\n])*?/[gim]*(?=\\s|\\W|$)"
        } ]
    }, {
        cN: "property",
        b: "@" + c
    }, {
        b: "`",
        e: "`",
        eB: !0,
        eE: !0,
        sL: "javascript"
    } ];
    return e.c = f, {
        aliases: [ "coffee", "cson", "iced" ],
        k: b,
        c: f.concat([ {
            cN: "comment",
            b: "###",
            e: "###"
        }, a.HCM, {
            cN: "function",
            b: "(" + c + "\\s*=\\s*)?(\\(.*\\))?\\s*\\B[-=]>",
            e: "[-=]>",
            rB: !0,
            c: [ d, {
                cN: "params",
                b: "\\(",
                rB: !0,
                c: [ {
                    b: /\(/,
                    e: /\)/,
                    k: b,
                    c: [ "self" ].concat(f)
                } ]
            } ]
        }, {
            cN: "class",
            bK: "class",
            e: "$",
            i: /[:="\[\]]/,
            c: [ {
                bK: "extends",
                eW: !0,
                i: /[:="\[\]]/,
                c: [ d ]
            }, d ]
        }, {
            cN: "attribute",
            b: c + ":",
            e: ":",
            rB: !0,
            eE: !0,
            r: 0
        } ])
    };
}), hljs.registerLanguage("nginx", function(a) {
    var b = {
        cN: "variable",
        v: [ {
            b: /\$\d+/
        }, {
            b: /\$\{/,
            e: /}/
        }, {
            b: "[\\$\\@]" + a.UIR
        } ]
    }, c = {
        eW: !0,
        l: "[a-z/_]+",
        k: {
            built_in: "on off yes no true false none blocked debug info notice warn error crit select break last permanent redirect kqueue rtsig epoll poll /dev/poll"
        },
        r: 0,
        i: "=>",
        c: [ a.HCM, {
            cN: "string",
            c: [ a.BE, b ],
            v: [ {
                b: /"/,
                e: /"/
            }, {
                b: /'/,
                e: /'/
            } ]
        }, {
            cN: "url",
            b: "([a-z]+):/",
            e: "\\s",
            eW: !0,
            eE: !0
        }, {
            cN: "regexp",
            c: [ a.BE, b ],
            v: [ {
                b: "\\s\\^",
                e: "\\s|{|;",
                rE: !0
            }, {
                b: "~\\*?\\s+",
                e: "\\s|{|;",
                rE: !0
            }, {
                b: "\\*(\\.[a-z\\-]+)+"
            }, {
                b: "([a-z\\-]+\\.)+\\*"
            } ]
        }, {
            cN: "number",
            b: "\\b\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}(:\\d{1,5})?\\b"
        }, {
            cN: "number",
            b: "\\b\\d+[kKmMgGdshdwy]*\\b",
            r: 0
        }, b ]
    };
    return {
        aliases: [ "nginxconf" ],
        c: [ a.HCM, {
            b: a.UIR + "\\s",
            e: ";|{",
            rB: !0,
            c: [ {
                cN: "title",
                b: a.UIR,
                starts: c
            } ],
            r: 0
        } ],
        i: "[^\\s\\}]"
    };
}), hljs.registerLanguage("json", function(a) {
    var b = {
        literal: "true false null"
    }, c = [ a.QSM, a.CNM ], d = {
        cN: "value",
        e: ",",
        eW: !0,
        eE: !0,
        c: c,
        k: b
    }, e = {
        b: "{",
        e: "}",
        c: [ {
            cN: "attribute",
            b: '\\s*"',
            e: '"\\s*:\\s*',
            eB: !0,
            eE: !0,
            c: [ a.BE ],
            i: "\\n",
            starts: d
        } ],
        i: "\\S"
    }, f = {
        b: "\\[",
        e: "\\]",
        c: [ a.inherit(d, {
            cN: null
        }) ],
        i: "\\S"
    };
    return c.splice(c.length, 0, e, f), {
        c: c,
        k: b,
        i: "\\S"
    };
}), hljs.registerLanguage("apache", function(a) {
    var b = {
        cN: "number",
        b: "[\\$%]\\d+"
    };
    return {
        aliases: [ "apacheconf" ],
        cI: !0,
        c: [ a.HCM, {
            cN: "tag",
            b: "</?",
            e: ">"
        }, {
            cN: "keyword",
            b: /\w+/,
            r: 0,
            k: {
                common: "order deny allow setenv rewriterule rewriteengine rewritecond documentroot sethandler errordocument loadmodule options header listen serverroot servername"
            },
            starts: {
                e: /$/,
                r: 0,
                k: {
                    literal: "on off all"
                },
                c: [ {
                    cN: "sqbracket",
                    b: "\\s\\[",
                    e: "\\]$"
                }, {
                    cN: "cbracket",
                    b: "[\\$%]\\{",
                    e: "\\}",
                    c: [ "self", b ]
                }, b, a.QSM ]
            }
        } ],
        i: /\S/
    };
}), hljs.registerLanguage("cpp", function(a) {
    var b = {
        keyword: "false int float while private char catch export virtual operator sizeof dynamic_cast|10 typedef const_cast|10 const struct for static_cast|10 union namespace unsigned long throw volatile static protected bool template mutable if public friend do return goto auto void enum else break new extern using true class asm case typeid short reinterpret_cast|10 default double register explicit signed typename try this switch continue wchar_t inline delete alignof char16_t char32_t constexpr decltype noexcept nullptr static_assert thread_local restrict _Bool complex _Complex _Imaginary",
        built_in: "std string cin cout cerr clog stringstream istringstream ostringstream auto_ptr deque list queue stack vector map set bitset multiset multimap unordered_set unordered_map unordered_multiset unordered_multimap array shared_ptr abort abs acos asin atan2 atan calloc ceil cosh cos exit exp fabs floor fmod fprintf fputs free frexp fscanf isalnum isalpha iscntrl isdigit isgraph islower isprint ispunct isspace isupper isxdigit tolower toupper labs ldexp log10 log malloc memchr memcmp memcpy memset modf pow printf putchar puts scanf sinh sin snprintf sprintf sqrt sscanf strcat strchr strcmp strcpy strcspn strlen strncat strncmp strncpy strpbrk strrchr strspn strstr tanh tan vfprintf vprintf vsprintf"
    };
    return {
        aliases: [ "c", "h", "c++", "h++" ],
        k: b,
        i: "</",
        c: [ a.CLCM, a.CBCM, a.QSM, {
            cN: "string",
            b: "'\\\\?.",
            e: "'",
            i: "."
        }, {
            cN: "number",
            b: "\\b(\\d+(\\.\\d*)?|\\.\\d+)(u|U|l|L|ul|UL|f|F)"
        }, a.CNM, {
            cN: "preprocessor",
            b: "#",
            e: "$",
            k: "if else elif endif define undef warning error line pragma",
            c: [ {
                b: 'include\\s*[<"]',
                e: '[>"]',
                k: "include",
                i: "\\n"
            }, a.CLCM ]
        }, {
            cN: "stl_container",
            b: "\\b(deque|list|queue|stack|vector|map|set|bitset|multiset|multimap|unordered_map|unordered_set|unordered_multiset|unordered_multimap|array)\\s*<",
            e: ">",
            k: b,
            c: [ "self" ]
        }, {
            b: a.IR + "::"
        } ]
    };
}), hljs.registerLanguage("makefile", function(a) {
    var b = {
        cN: "variable",
        b: /\$\(/,
        e: /\)/,
        c: [ a.BE ]
    };
    return {
        aliases: [ "mk", "mak" ],
        c: [ a.HCM, {
            b: /^\w+\s*\W*=/,
            rB: !0,
            r: 0,
            starts: {
                cN: "constant",
                e: /\s*\W*=/,
                eE: !0,
                starts: {
                    e: /$/,
                    r: 0,
                    c: [ b ]
                }
            }
        }, {
            cN: "title",
            b: /^[\w]+:\s*$/
        }, {
            cN: "phony",
            b: /^\.PHONY:/,
            e: /$/,
            k: ".PHONY",
            l: /[\.\w]+/
        }, {
            b: /^\t+/,
            e: /$/,
            c: [ a.QSM, b ]
        } ]
    };
});
//# sourceMappingURL=highlight.pack.js.map