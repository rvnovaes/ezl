class CustomMessage {
  constructor() {
    this.el = $('#custom-messages')
    this.storageKey = 'custom-messages'
    this.messagesTemplate = ``
    this.onClosePage();
    this.isRefrash = false;
    this.onRefrash();
  }

  get storeMessages() {
    return JSON.parse(localStorage.getItem(this.storageKey)) || []
  }

  set storeMessages(messages) {
    localStorage.setItem(this.storageKey, JSON.stringify(messages))
  }

  addMessage(message) {
    message.visualized = false;
    let messages = this.storeMessages
    if (!this.findMessage(message.id)) {
      messages.push(message)
    }
    this.storeMessages = messages
  }

  updateMessage(message) {
    let newMessages = []
    let messages = this.storeMessages;
    messages.forEach((storeMessage) => {
      if (storeMessage.id == message.id) {
        storeMessage = message
      }
      newMessages.push(storeMessage)
    })
    this.storeMessages = newMessages;
  }

  setVisualizedMessage(idMessage) {
    let message = this.findMessage(idMessage)
    message.visualized = true
    this.updateMessage(message)
  }

  findMessage(idMessage) {
    let messages = this.storeMessages.filter(message => message.id == idMessage);
    if (messages.length > 0) {
      return messages.reduce(message => message)
    }
    return undefined
  }

  onCloseMessage() {
    let self = this
    $('.message-alert').on('close.bs.alert', function () {
      const idMessage = $(this).attr('data-message');
      self.setVisualizedMessage(idMessage)
    })
  }
  getLinkButton(message) {
    let linkButton = ''
    if (message.link) {
      linkButton = `                 
        <div class="row">
          <div class="col-md-2 col-md-offset-5">
          <a href="${message.link}" class="btn btn-xs btn-default" target="_blank"> Veja mais!</a>
          </div>
        </div>      
      `
    }
    return linkButton
  }

  loadMessages() {
    if (localStorage.getItem('ezl-count-pages') <= 1) {
      fetch('/custom_messages/').then(response => {
        response.json()
          .then(result => {
            for (let message of result) {
              let storedMessage = this.findMessage(message.id)
              if (!storedMessage || storedMessage.visualized === false) {
                this.messagesTemplate += `
                <div class="alert alert-info">    
                <button type="button" class="close" data-dismiss="alert" aria-label="Close"> <span aria-hidden="true">×</span>
                </button>  
                  <i class="fa fa-2x fa-check-circle" aria-hidden="true"> </i>  
                  <strong>${message.message}</strong>                                    
                  ${this.getLinkButton(message)}                               
                </div>                                                                  
                `
                this.addMessage(message)
              }
            }
            this.el.append(this.messagesTemplate)
            this.onCloseMessage()
          })
      })
    }
  }

  onRefrash(){
    let self=this;
    $(document).on('keydown', function(e){
      const key = e.which;
      if(key === 116) {
        self.isRefrash = true
      }
    })
  }
  onClosePage() {
    let self = this;  
    $(window).unload(function () {
      if (parseInt(localStorage.getItem('ezl-count-pages')) === 1 && !self.isRefrash) {
        localStorage.removeItem(self.storageKey)
      }      
    })
  }
}