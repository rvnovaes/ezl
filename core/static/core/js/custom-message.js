class CustomMessage {  
  constructor() {
    this.el = $('#custom-messages')
    this.messagesTemplate = ``
  }
  loadMessages() {
    fetch('/custom_messages/').then(response => {
      response.json()
        .then(result => {
          for (let message of result) {
            this.messagesTemplate += `
            <div class="alert alert-info alert-dismissible" role="alert">
              <button type="button" class="close" data-dismiss="alert" aria-label="Fechar">
                <span aria-hidden="false">&times;</span>
              </button>
              <span>${message.message}</span>
              <br/>
              <strong>
                <a href="${message.link}" target="_blank">Veja mais!</a>
              </strong>
            </div>            
            `
          }
          this.el.append(this.messagesTemplate)
        })
    })
  }
}