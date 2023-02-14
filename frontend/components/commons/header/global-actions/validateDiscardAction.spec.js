import { shallowMount } from "@vue/test-utils";
import ValidateDiscardActionComponent from "./ValidateDiscardAction";

let wrapper = null;
const options = {
  stubs: ["base-checkbox", "annotation-label-selector", "base-button"],
  directives: {
    badge() {
      /* stub */
    },
  },
  propsData: {
    datasetId: ["owner", "name"],
    datasetTask: "TextClassification",
    visibleRecords: [
      {
        id: "b5a23810-10e9-4bff-adf3-447a45667299",
        metadata: {},
        annotation: {
          agent: "recognai",
          labels: [
            {
              class: "Aplazamiento de pago",
              score: 1,
            },
          ],
        },
        status: "Edited",
        selected: true,
        vectors: {},
        last_updated: "2023-02-14T13:38:00.319183",
        search_keywords: [],
        inputs: {
          text: "Esto es un registro sin predicciones ni anotaciones",
        },
        multi_label: true,
        currentAnnotation: {
          agent: "recognai",
          labels: [
            {
              class: "Aplazamiento de pago",
              score: 1,
            },
            {
              class: "Alcantarillado/Pluviales",
              score: 1,
            },
          ],
        },
        originStatus: "Discarded",
      },
      {
        id: "llamadas_correos_1238",
        metadata: {
          Fuente: "Correo",
        },
        prediction: {
          agent: "facsa_categories_v4",
          labels: [
            {
              class: "Otros",
              score: 0.7129160762,
            },
            {
              class: "Problema calidad agua",
              score: 0.0819710568,
            },
            {
              class: "Calidad del servicio",
              score: 0.0295235571,
            },
            {
              class: "Cortes falta de pago",
              score: 0.0239840839,
            },
            {
              class: "Alcantarillado/Pluviales",
              score: 0.0225764699,
            },
            {
              class: "Contratación",
              score: 0.013704461000000001,
            },
            {
              class: "Solicitan presencia personal FACSA instalación",
              score: 0.0132667627,
            },
            {
              class: "Consulta administrativa oficinas",
              score: 0.012263773,
            },
            {
              class: "Baja presión",
              score: 0.0107420115,
            },
            {
              class: "Funcionamiento del contador",
              score: 0.0099040149,
            },
            {
              class: "Recibos",
              score: 0.0091423625,
            },
            {
              class: "Reposición obra civil",
              score: 0.0085537238,
            },
            {
              class: "Filtración en garaje/bajo",
              score: 0.0082879839,
            },
            {
              class: "Fuga en la vía pública",
              score: 0.0069583142,
            },
            {
              class: "Información/Consultas",
              score: 0.0060733184,
            },
            {
              class: "Vulnerabilidad",
              score: 0.0049630683,
            },
            {
              class: "No tiene agua",
              score: 0.0042145588000000005,
            },
            {
              class: "Facturación errónea",
              score: 0.0037822824000000002,
            },
            {
              class: "Refacturación por fuga",
              score: 0.0030815087,
            },
            {
              class: "Atención recibida",
              score: 0.0030129601000000003,
            },
            {
              class: "Error de lectura",
              score: 0.0026326664000000002,
            },
            {
              class: "Fuga en instalación interior",
              score: 0.0024313715,
            },
            {
              class: "Rotura provocada",
              score: 0.0015803818000000001,
            },
            {
              class: "Presupuestos",
              score: 0.0011857918000000001,
            },
            {
              class: "Protección de datos",
              score: 0.0009309166,
            },
            {
              class: "Aplazamiento de pago",
              score: 0.0006013829,
            },
            {
              class: "descartado",
              score: 0.0005980578,
            },
            {
              class: "Reparto de correspondencia",
              score: 0.0005848766,
            },
            {
              class: "Solicitan cierre agua maniobras instalación abonado",
              score: 0.0005321669,
            },
            {
              class: "Alta",
              score: 0,
            },
            {
              class: "Baja",
              score: 0,
            },
            {
              class: "Cambio de titular",
              score: 0,
            },
          ],
        },
        annotation: {
          agent: "recognai",
          labels: [
            {
              class: "Alcantarillado/Pluviales",
              score: 1,
            },
            {
              class: "Contratación",
              score: 1,
            },
            {
              class: "Problema calidad agua",
              score: 1,
            },
            {
              class: "Funcionamiento del contador",
              score: 1,
            },
          ],
        },
        status: "Validated",
        selected: false,
        vectors: {},
        last_updated: "2023-02-14T12:35:27.656875",
        search_keywords: [],
        inputs: {
          text: "ANULACION TEMA CONTRAINCENDIOS NAVE SANTA Nº4 ROBERTO SURNAME-JORGE BADENES\n\nEscolta verificam que el que es l’aigua normal si va a\nnom nostre i tenim aigua en esta nau, per favor, jo crec que si, crec que es\nnau nº 4 i si paga jo l’aigua, pero verificameu per favor, el\ncontraincendis eixe, DONEM DE BAIXA!! No sabemn si la alquilarem ni si el\nproper negoci li fara falta, aixi que anulem-lo en cas de alquiler algu que li\nfage falta…pues ja seu pagara ell…el inquilino…com va fer\nJorge en el seu dia, ok?\nORDEN ANULACION, EN CASO DE QUE HAYA CONTADOR MINIMO DE\nFACSA AGUA QUE ES LO UNICO QUE QUEREMOS.\nGRACIAS\nVanessa SURNAME\nROBERTO SURNAME SL\nTelf. PHONE_NUMBER\nwww.rserrano.com\nEste correo electronico y, en su caso,\ncualquier archivo adjunto al mismo, contiene informacion de caracter\nconfidencial exclusivamente dirigida a su destinatario. Queda prohibida su\ndivulgacion, copia o distribucion a terceros sin la previa autorizacion escrita\nde ROBERTO SURNAME SL. En el caso de haber recibido este correo electronico por\nerror, por favor, eliminelo de inmediato y rogamos nos notifique esta\ncircunstancia mediante reenvio a la direccion electronica del remitente. De\nconformidad con lo establecido en las normativas vigentes de Proteccion de\nDatos a nivel nacional y europeo, ROBERTO SURNAME SL garantiza la adopcion de\nlas medidas tecnicas y organizativas necesarias para asegurar el tratamiento\nconfidencial de los datos de caracter personal. Asi mismo le informamos que su\ndireccion de email ha sido recabada del propio interesado o de fuentes de\nacceso publico, y esta incluida en nuestros ficheros con la finalidad de\nmantener contacto con usted para el envio de comunicaciones sobre nuestro\nproductos y servicios mientras exista un interes mutuo para ello o una relacion\nnegocial o contractual. No obstante, usted puede ejercer sus derechos de\nacceso, rectificacion y supresion de sus datos, asi como los derechos de\nlimitacion y oposicion a su tratamiento o solicitar mas informacion sobre\nnuestra politica de privacidad utilizando la siguiente informacion:\nResponsable: ROBERTO SURNAME SL\nDireccion: PARTIDA\nLA TORRETA\n,\nNAVE 9. 12110, Alcora (Castellon), Espana\nTelefono: PHONE_NUMBER\nE-mail:\nEMAIL_ADDRESS\nSi considera que el tratamiento no se ajusta a la normativa vigente de\nProteccion de Datos, podra presentar una reclamacion ante la autoridad de\ncontrol: Agencia Espanola de Proteccion de Datos (\nhttps://www.agpd.es\n)",
        },
        multi_label: true,
        currentAnnotation: {
          agent: "recognai",
          labels: [
            {
              class: "Alcantarillado/Pluviales",
              score: 1,
            },
            {
              class: "Contratación",
              score: 1,
            },
            {
              class: "Problema calidad agua",
              score: 1,
            },
            {
              class: "Funcionamiento del contador",
              score: 1,
            },
          ],
        },
        originStatus: "Validated",
      },
    ],
    isMultiLabel: true,
  },
};

beforeEach(() => {
  wrapper = shallowMount(ValidateDiscardActionComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});
describe("ValidateDiscardAction", () => {
  it("render the component", () => {
    expect(wrapper.is(ValidateDiscardActionComponent)).toBe(true);
  });
  it("render a validate button", () => {
    const validateButtonId = "validateButton";
    testIfValidateButtonIsRendered(validateButtonId);
  });
  it.skip("render a badge on a validate button if there is pending records", () => {
    //FIXME - test that the validate button contains a v-badge attributes if there is any record with pending states
    //NOTE - a record in pending status have the attribute "status:'Edited'"
    testIfThereIsPendingStatus(true);
  });
});

const testIfValidateButtonIsRendered = (validateButtonId) => {
  const validateButtonWrapper = wrapper.find(`#${validateButtonId}`);
  expect(validateButtonWrapper.exists()).toBe(true);
};

const testIfThereIsPendingStatus = (isPendingStatus) => {
  expect(wrapper.vm.isAnyPendingStatusRecord).toBe(isPendingStatus);
};
