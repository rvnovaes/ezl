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

  showSideBarNotifications() {
    $('.right-sidebar').show()
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
    $('.close').on('click', function (el) {
      const idMessage = $(this).attr('data-message');
      self.setVisualizedMessage(idMessage)
      $(this).parent().parent().hide()

    })
  }

  getLinkButton(message) {
    let linkButton = ''
    if (message.link) {
      linkButton = `        
        <a href="${message.link}" target="_blank" class="btn btn btn-rounded btn-default btn-outline m-r-5">
          <i class="ti-check text-success m-r-5"></i>Veja mais
        </a>               
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
              console.log(message)
              let storedMessage = this.findMessage(message.id)
              if (!storedMessage || storedMessage.visualized === false) {
                this.showSideBarNotifications();
                this.messagesTemplate += `
                <div class="comment-body">
                  <div class="user-img"> 
                    <i class="fa fa-2x fa-check-circle text-success"></i>          
                  </div>
                  <div class="mail-contnet">
                    <button type="button" data-message="${message.id}"class="close" aria-label="Close"> <span aria-hidden="true">×</span>                    
                    </button>
                    <h5>${message.title}</h5>                              
                    <span class="mail-desc">
                      ${message.message}  
                    </span> 
                    ${this.getLinkButton(message)}
                  </div>
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

  onRefrash() {
    let self = this;
    $(document).on('keydown', function (e) {
      const key = e.which;
      if (key === 116) {
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