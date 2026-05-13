/*******************************************************************************
* Copyright (C) 2025 Microchip Technology Inc. and its subsidiaries.
*
* Subject to your compliance with these terms, you may use Microchip software
* and any derivatives exclusively with Microchip products. It is your
* responsibility to comply with third party license terms applicable to your
* use of third party software (including open source software) that may
* accompany Microchip software.
*
* THIS SOFTWARE IS SUPPLIED BY MICROCHIP "AS IS". NO WARRANTIES, WHETHER
* EXPRESS, IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE, INCLUDING ANY IMPLIED
* WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A
* PARTICULAR PURPOSE.
*
* IN NO EVENT WILL MICROCHIP BE LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE,
* INCIDENTAL OR CONSEQUENTIAL LOSS, DAMAGE, COST OR EXPENSE OF ANY KIND
* WHATSOEVER RELATED TO THE SOFTWARE, HOWEVER CAUSED, EVEN IF MICROCHIP HAS
* BEEN ADVISED OF THE POSSIBILITY OR THE DAMAGES ARE FORESEEABLE. TO THE
* FULLEST EXTENT ALLOWED BY LAW, MICROCHIP'S TOTAL LIABILITY ON ALL CLAIMS IN
* ANY WAY RELATED TO THIS SOFTWARE WILL NOT EXCEED THE AMOUNT OF FEES, IF ANY,
* THAT YOU HAVE PAID DIRECTLY TO MICROCHIP FOR THIS SOFTWARE.
*******************************************************************************/

/*******************************************************************************
  Application BLE Profile Source File

  Company:
    Microchip Technology Inc.

  File Name:
    app_trsps_handler.c

  Summary:
    This file contains the Application BLE functions for this project.

  Description:
    This file contains the Application BLE functions for this project.
 *******************************************************************************/


// *****************************************************************************
// *****************************************************************************
// Section: Included Files
// *****************************************************************************
// *****************************************************************************
#include "app_trsps_handler.h"
#include "osal/osal_freertos_extend.h"
#include "peripheral/sercom/usart/plib_sercom0_usart.h"
#include "app.h"
#include "../app_modules/ble_diag_bridge/ble_diag_bridge.h"
#include <stdio.h>

#define SERCOM_TX_BUFFER_SIZE               500

// *****************************************************************************
// *****************************************************************************
// Section: Global Variables
// *****************************************************************************
// *****************************************************************************


// *****************************************************************************
// *****************************************************************************
// Section: Functions
// *****************************************************************************
// *****************************************************************************

void APP_TrspsEvtHandler(BLE_TRSPS_Event_T *p_event)
{
    switch(p_event->eventId)
    {
        case BLE_TRSPS_EVT_CTRL_STATUS:
        {
            /* TODO: implement your application code.*/
        }
        break;
        
        case BLE_TRSPS_EVT_TX_STATUS:
        {
            /* TODO: implement your application code.*/
        }
        break;

        case BLE_TRSPS_EVT_CBFC_ENABLED:
        {
            /* TODO: implement your application code.*/
        }
        break;
        
        case BLE_TRSPS_EVT_CBFC_CREDIT:
        {
            /* TODO: implement your application code.*/
        }
        break;
        
        case BLE_TRSPS_EVT_RECEIVE_DATA:
        {
            uint16_t data_len;
            uint8_t *data;

            BLE_TRSPS_GetDataLength(p_event->eventField.onReceiveData.connHandle, &data_len);
            data = OSAL_Malloc(data_len);
            if(data == NULL)
                break;
            BLE_TRSPS_GetData(p_event->eventField.onReceiveData.connHandle, data);
            BLE_DIAG_OnDataReceived(data, data_len);
            OSAL_Free(data);
        }
        break;
        
        case BLE_TRSPS_EVT_VENDOR_CMD:
        {
            /* TODO: implement your application code.*/
        }
        break;

        case BLE_TRSPS_EVT_ERR_UNSPECIFIED:
        {
            /* TODO: implement your application code.*/
        }
        break;

        case BLE_TRSPS_EVT_ERR_NO_MEM:
        {
            /* TODO: implement your application code.*/
        }
        break;

        default:
        break;
    }
}