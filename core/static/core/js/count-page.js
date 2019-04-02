class CountPage {
    constructor() {
        this.key = 'ezl-count-pages'
        this.onLoadPage()
        this.onClosePage()
    }
    getPages() {
        return parseInt(localStorage.getItem(this.key)) || 0
    }
    onLoadPage() {
        localStorage.setItem(this.key, this.getPages() + 1)
    }
    onClosePage() {        
        let self = this;
        $(window).unload(function (){
            if (self.getPages()> 0){
                this.localStorage.setItem(self.key, self.getPages() -1 )            
            }                        
        })        
    }
}