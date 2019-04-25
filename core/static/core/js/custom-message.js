class CustomMessage {
  constructor() {
    this.el = $('#custom-messages')
    this.storageKey = 'custom-messages'
    this.messagesTemplate = ``    
    this.messagesShow = [];
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
    message.visualized = new Date().toLocaleDateString()
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
      self.messagesShow = self.messagesShow.filter(message => message != idMessage)      
      self.setVisualizedMessage(idMessage)
      $(this).parent().parent().hide()      
      if (!self.messagesShow.length) {
        $('.right-sidebar').hide()
      }
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
    fetch('/custom_messages/').then(response => {
      response.json()
        .then(result => {                        
          for (let message of result) {
            let storedMessage = this.findMessage(message.id)            
            if (!storedMessage || storedMessage.visualized !== new Date().toLocaleDateString()) {
              this.showSideBarNotifications();
              this.messagesShow.push(message.id);                
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