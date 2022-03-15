class Check:
    def check(id,pw,age,height,weight):
        #空白チェック
        if (id=='') or (pw =='') or (age =='') or (height =='') or (weight ==''):
            msg='全ての項目を入力してください'
            return msg
        #型チェック
        try :
            type(int(age)) is int
            type(int(height)) is int
            type(int(weight)) is int
        except ValueError:
            msg='数字入力すべき所に数字以外を入力しています'
            return msg

        #型チェック完了後型変換
        age=int(age)
        height=int(height)
        weight=int(weight)

        #数値チェック
        if age>100:
            msg='年齢が高すぎます'
            return msg
        elif height>200:
            msg='身長が高すぎます'
            return msg
        elif weight>200:
            msg='体重が重すぎます'
            return msg


