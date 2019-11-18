'use strict';

var js = {

    download_list: [], 
    error_on: false, 
    favorite: '', 
    order: 'NEWEST',
    query: '',
    yellow_error: '#FFFFCD', 

    //  Bind events
    init: function(){

        //  Click
        document.addEventListener('click', this.click.bind(this));

        //  Keyup
        var t = document.querySelectorAll('input[type="text"]');
        
        for (let x = 0, l = t.length; x < l; x++){
            t[x].addEventListener('keyup', this.keyup.bind(this));
        }

        //  Form Submit
        for (let x = 0, l = document.forms.length; x < l; x++){
            document.forms[x].addEventListener('submit', this.form_submit.bind(this));
        }

        //  Update downloads each 5 seconds
        this.downlist_spin();
        
    },

    //  Handles all the clicks. Goes down on parent elements
    //  until find a dataset with a method's name
    //  or until reaches a null <html>
    click: function(event){        

        var t = event.target, d = [t.dataset[0]];

        while (!d[0] && t){
            t = t.parentElement;            
            if (t) d[0] = t.dataset[0];
        }

        if (d[0]){

            for (let x = 1; x <= 4; x++){
                d.push(t.dataset[x]);
            }

            if (d[0] in this){
                this[d[0]](t, d);
            }

        }

        if (this.error_on){
            this.error_on = false;
            document.getElementById('error').style.display = 'none';
        }
        
    },

    downlist_add: function(uid){

        console.log(uid);
        //var downlist = this.downlist_get();        
        //downlist.push({'uid': uid, 'data': [], 'err': null});        
        //localStorage.setItem('downlist', JSON.stringify(downlist));
        
    }, 

    downlist_del: function(uid){

    },

    downlist_get: function(){

        var downlist = localStorage.getItem('downlist');
        return downlist ? JSON.parse(downlist) : []
        
    },

    downlist_item: function(dl){

        return `
        <div class="item" id="dl_${dl.uid}">
            <div class="info">
                <ul>
                    <li>${dl.host}</li>
                    <li>${dl.name}</li>
                </ul>
                <span>&times;</span>
                </div>
                <div class="bar">
                    <div class="per" style="width:${dl.per}%"></div>
                    <div class="txt">${dl.info}</div>
                </div>
        </div>`;
        
    }, 

    downlist_spin: function(){
        
        var downlist = this.downlist_get();

        if (downlist.length){

            var check = [], del = [], args = [];
            
            for (let x = 0, l = downlist.length; x < l; x++){
                uidpid = downlist[x]['uid'] + ',' + downlist[x]['pid'];
                downlist[x]['del'] ? del.push(uidpid) : check.push(uidpid);
            }

            if (check) args.push('check=' + check.join('|'));
            if (del) args.push('del=' + del.join('|'));
            
        }else{
            setTimeout(this.downlist_spin.bind(this), 5000);            
        }
        
    }, 
    
    downlist_update: function(data){

    }, 
    
    //  Returns [x, y, w, h] of an element
    el_coord: function(el){
        
        var r = el.getBoundingClientRect();
        
        return [
            el.offsetWidth,
            el.offsetHeight,
            r.top + window.scrollY,
            r.left + window.scrollX,
        ];
        
    },

    error: function(e){

        var error_src = document.getElementById('error');
        error_src.querySelector('div:last-child').innerHTML = 'ERROR:<br />' + e;
        error_src.style.display = 'flex';
        this.error_on = true;
        
    }, 
    
    error_bgblink: async function(el){

        var bg_start = window.getComputedStyle(el).getPropertyValue('backgroundColor'),
            bg_ori = bg_start,
            bg = bg_start;

        for (let x = 0; x < 8; x++){
            
            var bg = (bg == bg_ori) ? this.yellow_error : bg_ori;
            el.style.backgroundColor = bg;
            await this.sleep(100);
            
        }
        
    }, 

    //  Submit all forms through XHR
    form_submit: function(event){

        event.preventDefault();
        var name = event.target.name;

        //  Add new download
        if (name == 'add'){
            
            var url = event.target.url.value,
                pla = event.target.pla.value;

            if (!url){
                this.error('Enter a valid URL address');
            }else{

                this.xhr_submit('POST', '/add', {url: url, pla: pla}, function(r){
                    this.downlist_add(r.uid);                    
                }.bind(this));
                                
            }
            
        }

    },

    //  Keyup
    keyup: function(event){
        
        //console.log(this.el_coord(event.target));
        //console.log(event.target.value);
        
    }, 

    //  Toggle the download manager window
    manage_toggle: function(target, d){

        var el = document.getElementById('manage'),
            css = window.getComputedStyle(el),
            display = css.getPropertyValue('display') == 'none' ? 'block' : 'none';

        el.style.display = display;
        
    },

    newold_toggle: function(target){

        this.order = this.order == 'NEWEST' ? 'OLDEST' : 'NEWEST';
        target.innerHTML = this.order;
        
    },

    sleep: function(ms){
        return new Promise(resolve => setTimeout(resolve, ms));
    },

    xhr_submit: function(method, location, params, done){

        var xhr = new XMLHttpRequest();
        xhr.open(method, location, true);

        if (method == 'POST'){
            xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
            params = Object.entries(params).map(([k, v]) => `${k}=${encodeURIComponent(v)}`).join('&');
        }
        
        xhr.onload = function(e){
            
            if (xhr.status == 200){                
                var r = JSON.parse(xhr.response);
                r['error'] ? this.error(r['error']) : done(r);
            }else{
                this.error('Server Request Failure');
            }
            
        }.bind(this);
        
        xhr.onerror = function(e){
            this.error('Server Request Failure');
        }.bind(this);
        
        xhr.send(method == 'POST' ? params : null);
        
    }
    
}.init();
